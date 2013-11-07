import codecs
from bs4 import BeautifulSoup
from util import get

def write_csv(outfile, results, headers):
    print "Writing {0}".format(outfile.name)
    outfile.write("{0}\n".format(",".join(headers)))
    for result in results:
        outfile.write(u'{0}, {1}, {2}, {3}, "{4}", "{5}"\n'.format(*result))

def parse_page(soup):
    days = soup.find_all("table", "tablehead")
    results = []
    for day in days:
        date = day.tr.text
        for game in day.find_all("tr")[2:]:
            cells = game.find_all("td")

            status = cells[0].text
            #skip in-progress games
            if "FT" not in status: continue

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

def get_espn(league, url, headers, get_all_history=False):
    r = get(url)

    soup = BeautifulSoup(r.text)
    season = soup.h2.text.split(" ")[0]
    results = parse_page(soup)

    while 1:
        previous = soup.find("p", "prev-next-links").a

        # If we reach the final page of ESPN's available history, break
        if not "Previous" in previous.text: break

        url = previous["href"]

        print "getting previous page %s" % url
        r = get(url)

        soup = BeautifulSoup(r.text)
        # If we find we've reached a new season's data
        if soup.h2.text.split(" ")[0] != season:
            if get_all_history:
                season_f = "{0}_{1}".format(season[2:4], season[5:7])
                out = codecs.open("data/{0}_{1}.csv".format(league, season_f), 'w', "utf8")
                write_csv(out, results, headers)

                season = soup.h2.text.split(" ")[0]
                print "found season: {0}".format(season)
                results = []
            else:
                break

        results += parse_page(soup)

    season_f = "{0}_{1}".format(season[2:4], season[5:7])
    out = codecs.open("data/{0}_{1}.csv".format(league, season_f), 'w', "utf8")
    write_csv(out, results, headers)

if __name__=="__main__":
    league = ("home", "homescore", "awayscore", "away", "date", "location")
    tourney = ("home", "homescore", "awayscore", "away", "date", "group")
    urls = [
        ("bpl", "http://espnfc.com/results/_/league/eng.1/barclays-premier-league", league),
        ("bundesliga", "http://espnfc.com/results/_/league/ger.1/german-bundesliga", league),
        ("seriea", "http://espnfc.com/results/_/league/ita.1/italian-serie-a", league),
        ("laliga", "http://espnfc.com/results/_/league/esp.1/spanish-la-liga", league),
        ("ligue1", "http://espnfc.com/results/_/league/fra.1/french-ligue-1", league),
        ("cl", "http://espnfc.com/results/_/league/uefa.champions/uefa-champions-league", tourney),
        ("europa", "http://espnfc.com/results/_/league/uefa.europa/uefa-europa-league", tourney),
    ]

    for league, url, headers in urls:
        print "getting espn %s" % url
        get_espn(league, url, headers)
