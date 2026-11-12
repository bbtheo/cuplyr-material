# Read vs compute split for the p1_nopush pipeline at 1e8 rows (narrow table), dplyr and data.table.
# Same code as the benchmark: arrow::read_parquet(col_select = cols), then the p1_nopush verbs.
.libPaths(c("/home/theo/cuplyr-material/benchmarks/rlib", .libPaths()))
f <- "/home/theo/cuplyr-material/benchmarks/parquet-pipeline/data/fact-narrow-100000000.parquet"
out <- "/home/theo/cuplyr-material/social/parquet-to-summary/build/split.csv"
cols <- c("store", "channel", "price", "qty", "discount")

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

timed <- function(expr) { gc(); system.time(r <- expr)[["elapsed"]] }
rows <- list()
for (rep in 0:5) {
  t_read <- timed(x <- arrow::read_parquet(f, col_select = cols))
  t_dplyr <- timed(dplyr_compute(x))
  rows[[length(rows) + 1]] <- data.frame(engine = "dplyr", rep = rep, read = t_read, compute = t_dplyr)
  rm(x); gc()
  t_read <- timed(x <- arrow::read_parquet(f, col_select = cols))
  t_dt <- timed(dt_compute(x))
  rows[[length(rows) + 1]] <- data.frame(engine = "data.table", rep = rep, read = t_read, compute = t_dt)
  rm(x); gc()
}
res <- do.call(rbind, rows)
write.csv(res, out, row.names = FALSE)
print(aggregate(cbind(read, compute) ~ engine, data = res[res$rep >= 1, ], FUN = median))
