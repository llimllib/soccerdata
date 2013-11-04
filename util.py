import time

def get(url, retries=10):
    #TODO: backoff
    r = requests.get(url)
    sleep = .1
    for _ in range(retries):
        if r.status_code == 200:
            return r
        sleep *= 2
        print "retrying in {0}".format(sleep)
        time.sleep(sleep)
        r = requests.get(url)
    raise Exception("GET failed.\nstatus: {0}\nurl: {1}".format(r.status_code, url))
