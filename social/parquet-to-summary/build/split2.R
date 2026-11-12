# Redo the read/compute split with arrow's lazy (ALTREP) columns forced inside the "read" step,
# and record CPU time next to elapsed time.
.libPaths(c("/home/theo/cuplyr-material/benchmarks/rlib", .libPaths()))
f <- "/home/theo/cuplyr-material/benchmarks/parquet-pipeline/data/fact-narrow-100000000.parquet"
cols <- c("store", "channel", "price", "qty", "discount")
out <- "/home/theo/cuplyr-material/social/parquet-to-summary/build/split2.csv"
cat("arrow.use_altrep default:", getOption("arrow.use_altrep"), "\n")

dplyr_compute <- function(x) {
  x |>
    dplyr::filter(price >= 150, channel != "phone") |>
    dplyr::mutate(revenue = price * qty * (1 - discount)) |>
    dplyr::group_by(store, channel) |>
    dplyr::summarise(n = dplyr::n(), revenue = sum(revenue, na.rm = TRUE),
                     avg_price = mean(price), max_qty = max(qty), .groups = "drop")
}
dt_compute <- function(x) {
  data.table::setDT(x)
  x[price >= 150 & channel != "phone",
    .(n = .N, revenue = sum(price * qty * (1 - discount), na.rm = TRUE),
      avg_price = mean(price), max_qty = max(qty)), by = .(store, channel)]
}
tm <- function(expr) { gc(); t <- system.time(expr); c(el = t[["elapsed"]], cpu = t[["user.self"]] + t[["sys.self"]]) }

rows <- list()
for (alt in c(TRUE, FALSE)) {
  options(arrow.use_altrep = alt)
  for (rep in 0:4) for (eng in c("dplyr", "data.table")) {
    r <- tm(x <- arrow::read_parquet(f, col_select = cols))
    cmp <- tm(if (eng == "dplyr") dplyr_compute(x) else dt_compute(x))
    rows[[length(rows) + 1]] <- data.frame(altrep = alt, engine = eng, rep = rep,
      read_el = r[["el"]], read_cpu = r[["cpu"]], comp_el = cmp[["el"]], comp_cpu = cmp[["cpu"]])
    rm(x); gc()
  }
}
res <- do.call(rbind, rows)
write.csv(res, out, row.names = FALSE)
options(digits = 3)
print(aggregate(cbind(read_el, read_cpu, comp_el, comp_cpu) ~ altrep + engine, data = res[res$rep >= 1, ], FUN = median))
