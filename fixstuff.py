import glob

tofix = glob.glob("data/laliga*.csv")
for f in tofix:
    print "fixing %s" % f
    lines = open(f).readlines()
    out = file(f, 'w')
    out.write("home, homescore, awayscore, away, date, stadium\n")
    for line in lines:
        out.write(line)
