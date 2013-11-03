import requests, cPickle, os.path, codecs
from bs4 import BeautifulSoup

def write_bpl_csv(outfile, results):
    outfile.write("home, homescore, awayscore, away, date, time\n")
    for result in results:
        outfile.write("{0}, {1}, {2}, {3}, {4}, {5}\n".format(*result))

def bpl_13_14():
    if not os.path.isfile("results.pkl"):
        r = requests.get("http://www.premierleague.com/en-gb/matchday/results.html?paramComp_100=true&view=.dateSeason")
        assert r.status_code==200
        cPickle.dump(r.content, file("results.pkl", 'w'))

    content = cPickle.load(file("results.pkl"))
    soup = BeautifulSoup(content)
    groups = soup.find_all("table", "contentTable")
    results = []
    for group in groups:
        date = group.tr.text.strip()
        for game in group.find_all("tr")[1:]:
            time = game.find("td", "time").text.strip()
            home = game.find("td", "rHome").a.text.strip()
            away = game.find("td", "rAway").a.text.strip()

            score = game.find("td", "score").a.text.split("-")
            results.append((home, int(score[0]), int(score[1]), away, date, time))

    write_bpl_csv(file("data/bpl_13_14.csv", 'w'), results)

def bpl_season(season="2012-2013"):
    print "getting season {0}".format(season)
    url = "http://www.premierleague.com/en-gb/matchday/results.html?paramClubId=ALL&paramComp_8=true&paramSeason={0}&view=.dateSeason".format(season)
    print "from url {0}".format(url)

    r = requests.get(url)
    assert r.status_code==200

    soup = BeautifulSoup(r.content)
    groups = soup.find_all("table", "contentTable")
    results = []
    for group in groups:
        date = group.tr.text.strip()
        for game in group.find_all("tr")[1:]:
            time = game.find("td", "time").text.strip()
            home = game.find("td", "rHome").a.text.strip()
            away = game.find("td", "rAway").a.text.strip()

            score = game.find("td", "score").a.text.split("-")
            results.append((home, int(score[0]), int(score[1]), away, date, time))

    write_csv(file("data/bpl_{0}_{1}.csv".format(season[2:4], season[7:9]), 'w'), results)

def write_cl_csv(outfile, results):
    outfile.write("home, homescore, awayscore, away, date, group\n")
    for result in results:
        outfile.write(u"{0}, {1}, {2}, {3}, {4}, {5}\n".format(*result))

def parse_cl_page(soup):
    days = soup.find_all("table", "tablehead")
    results = []
    for day in days:
        date = day.tr.text
        for game in day.find_all("tr")[2:]:
            cells = game.find_all("td")
            home = cells[1].text
            result = cells[2].text
            away = cells[3].text
            group = cells[4].text

            try:
                homescore, awayscore = result.split("-")
            except ValueError:
                print "unable to parse game {0}".format(cells)
                continue

            results.append((home, homescore, awayscore, away, date, group))

    return results

def get(url, retries=5):
    r = requests.get(url)
    for _ in range(retries):
        if r.status_code == 200:
            return r
        print "retrying"
        r = requests.get(url)
    raise Exception("GET failed.\nstatus: {0}\nurl: {1}".format(r.status_code, url))

def champions_league():
    url = "http://espnfc.com/results/_/league/uefa.champions/uefa-champions-league?cc=5901"
    #the 2004/2005 data is missing some results. Starts here:
    url = "http://espnfc.com/results/_/league/uefa.champions/date/20050426/uefa-champions-league"
    #2003/2004
    #url = "http://espnfc.com/results/_/league/uefa.champions/date/20040526/uefa-champions-league"
    ##2002/2003
    #url = "http://espnfc.com/results/_/league/uefa.champions/date/20030528/uefa-champions-league"
    #2001/2002
    url = "http://espnfc.com/results/_/league/uefa.champions/date/20020515/uefa-champions-league"

    print "getting %s" % url
    r = get(url)

    soup = BeautifulSoup(r.content)
    season = soup.h2.text.split(" ")[0]
    results = parse_cl_page(soup)

    while 1:
        previous = soup.find("p", "prev-next-links").a
        if not "Previous" in previous.text: break
        url = previous["href"]

        print "getting %s" % url
        r = get(url)

        soup = BeautifulSoup(r.content)
        if soup.h2.text.split(" ")[0] != season:
            season_f = "{0}_{1}".format(season[2:4], season[5:7])
            out = codecs.open("data/cl_{0}.csv".format(season_f), 'w', "utf8")
            write_cl_csv(out, results)

            season = soup.h2.text.split(" ")[0]
            print "found season: {0}".format(season)
            results = []

        results += parse_cl_page(soup)

    season_f = "{0}_{1}".format(season[2:4], season[5:7])
    out = codecs.open("data/cl_{0}.csv".format(season_f), 'w', "utf8")
    write_cl_csv(out, results)


if __name__=="__main__":
    #bpl_13_14()
    #for season in range(1992, 2013):
    #    seasonstr = "{0}-{1}".format(season, season+1)
    #    bpl_season(seasonstr)
    champions_league()
