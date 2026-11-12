out <- "/home/theo/cuplyr-material/benchmarks/parquet-pipeline"
tm <- read.csv(file.path(out, "timings.csv"), stringsAsFactors = FALSE)
tm$quiet <- as.logical(tm$quiet); tm$ok <- as.logical(tm$ok)
tq <- tm[tm$rep >= 1 & tm$ok & tm$quiet, ]
med <- aggregate(secs ~ engine + variant + table + rows + cache, data = tq, FUN = median)
show <- function(tab, n, cache, vs = unique(med$variant)) {
  d <- med[med$table == tab & med$rows == n & med$cache == cache & med$variant %in% vs, ]
  w <- reshape(d, idvar = c("variant", "table", "rows", "cache"), timevar = "engine", direction = "wide")
  names(w) <- sub("^secs\\.", "", names(w))
  w[order(w$variant), c("variant", "cuplyr", "duckdb", "dplyr", "data.table")]
}
options(width = 200, digits = 3)
for (cache in c("warm", "cold")) { cat("\n== 1e8 narrow", cache, "\n"); print(show("narrow", 1e8, cache), row.names = FALSE) }
for (n in c(1e6, 1e7)) { cat("\n== p1_push narrow warm", n, "\n"); print(show("narrow", n, "warm", "p1_push"), row.names = FALSE) }
timed <- tm[tm$rep >= 1 & tm$ok, ]
cat("\ncalls", nrow(tm), "timed", nrow(timed), "not quiet", sum(!timed$quiet), "\n")
nq <- timed[!timed$quiet, ]
if (nrow(nq)) { print(nq[c("engine","variant","table","rows","cache","rep","secs","busy","kernel")], row.names = FALSE); cat("median foreign", median(nq$busy), "max", max(nq$busy), "median kernel", median(nq$kernel), "max", max(nq$kernel), "\n") }
cat("max foreign in quiet reps", max(tq$busy), "\n")
# wins and losses
cu <- med[med$engine == "cuplyr", ]; ot <- med[med$engine != "cuplyr", ]
best <- aggregate(secs ~ variant + table + rows + cache, data = ot, FUN = min)
m <- merge(cu, best, by = c("variant", "table", "rows", "cache"), suffixes = c("", "_best"))
m$ratio <- m$secs / m$secs_best
cat("\ncuplyr wins", sum(m$ratio < 1), "of", nrow(m), "; warm", sum(m$ratio < 1 & m$cache == "warm"), "of", sum(m$cache == "warm"), "; cold", sum(m$ratio < 1 & m$cache == "cold"), "of", sum(m$cache == "cold"), "\n")
print(table(m$variant[m$ratio >= 1], m$cache[m$ratio >= 1]))
cat("\nlosses by size:\n"); print(table(m$rows[m$ratio >= 1]))
cat("\nwall minutes by step (provenance):\n")
pv <- read.csv(file.path(out, "provenance.csv"), stringsAsFactors = FALSE)
pv$min <- as.numeric(difftime(as.POSIXct(pv$ended, format = "%Y-%m-%dT%H:%M:%OS"), as.POSIXct(pv$started, format = "%Y-%m-%dT%H:%M:%OS"), units = "mins"))
print(aggregate(min ~ step, data = pv, FUN = sum))
print(unique(pv[c("git_head", "bench_dirty", "cuplyr_commit", "cuplyr_dirty")]))
