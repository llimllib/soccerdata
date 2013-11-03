import requests, cPickle, os.path
from bs4 import BeautifulSoup

def write_csv(outfile, results):
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

    write_csv(file("data/bpl_13_14.csv", 'w'), results)

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

if __name__=="__main__":
    #bpl_13_14()
    for season in range(2007, 2013):
        seasonstr = "{0}-{1}".format(season, season+1)
        bpl_season(seasonstr)
