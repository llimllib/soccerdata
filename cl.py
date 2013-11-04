import requests, codecs
from bs4 import BeautifulSoup
from util import get

def write_cl_csv(outfile, results):
    outfile.write("home, homescore, awayscore, away, date, group\n")
    for result in results:
        outfile.write(u'{0}, {1}, {2}, {3}, "{4}", {5}\n'.format(*result))

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

def champions_league():
    url = "http://espnfc.com/results/_/league/uefa.champions/uefa-champions-league?cc=5901"

    print "getting %s" % url
    r = get(url)

    soup = BeautifulSoup(r.text)
    season = soup.h2.text.split(" ")[0]
    results = parse_cl_page(soup)

    while 1:
        previous = soup.find("p", "prev-next-links").a
        if not "Previous" in previous.text: break
        url = previous["href"]

        print "getting %s" % url
        r = get(url)

        soup = BeautifulSoup(r.text)
        if soup.h2.text.split(" ")[0] != season:
            #break

            #uncomment all this to download previous seasons' data
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
    champions_league()
