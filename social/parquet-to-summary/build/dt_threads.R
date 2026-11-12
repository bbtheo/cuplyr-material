# How many CPUs does data.table's compute step (p1_nopush, 1e8 rows) actually use?
.libPaths(c("/home/theo/cuplyr-material/benchmarks/rlib", .libPaths()))
library(data.table)
f <- "/home/theo/cuplyr-material/benchmarks/parquet-pipeline/data/fact-narrow-100000000.parquet"
x <- arrow::read_parquet(f, col_select = c("store", "channel", "price", "qty", "discount"))
setDT(x)
cat("getDTthreads():", getDTthreads(), "\n")

single <- function() x[price >= 150 & channel != "phone",
  .(n = .N, revenue = sum(price * qty * (1 - discount), na.rm = TRUE),
    avg_price = mean(price), max_qty = max(qty)), by = .(store, channel)]
stepwise <- function() {
  y <- x[price >= 150 & channel != "phone"]
  y[, revenue := price * qty * (1 - discount)]
  y[, .(n = .N, revenue = sum(revenue, na.rm = TRUE), avg_price = mean(price), max_qty = max(qty)),
    by = .(store, channel)]
}
meas <- function(fn, label, reps = 4) {
  fn()  # warm
  r <- t(vapply(seq_len(reps), function(i) { gc(); t <- system.time(fn()); c(t[["elapsed"]], t[["user.self"]] + t[["sys.self"]]) }, c(0, 0)))
  cat(sprintf("%-28s elapsed %.2f s  cpu %.2f s  => %.1f CPUs busy\n", label,
              median(r[, 1]), median(r[, 2]), median(r[, 2]) / median(r[, 1])))
}
for (n in c(12, 1)) {
  setDTthreads(n)
  meas(single, sprintf("single form, %2d threads", n))
  meas(stepwise, sprintf("stepwise form, %2d threads", n))
}
# the filter alone, to see which part is parallel
setDTthreads(12); meas(function() x[price >= 150 & channel != "phone", which = TRUE], "filter only, 12 threads")
setDTthreads(1);  meas(function() x[price >= 150 & channel != "phone", which = TRUE], "filter only,  1 thread")
