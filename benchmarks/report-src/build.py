import re

src = '/home/theo/cuplyr-material/benchmarks/report-src/template.md'
out_dir = '/home/theo/cuplyr-material/benchmarks/rolling/'
t = open(src).read()


def sub(m):
    body = open(out_dir + m.group(1)).read().strip('\n')
    return re.sub(r'^# Median tables\n+', '', body)


t = re.sub(r'\{\{([a-z\-\.]+)\}\}', sub, t)
open(out_dir + 'report.md', 'w').write(t)
print(len(t))
