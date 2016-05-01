import datetime
import json
import itertools

from mwclient import Site

NUM_CONTRIBUTIONS = 1000

site = Site("en.wikipedia.org",
            clients_useragent="Data generation bot run by User:APerson (apersonwiki@gmail.com)")

contributions = []
for contribution in itertools.islice(site.usercontributions("APerson", namespace=4), NUM_CONTRIBUTIONS):
    # The :6 trick is from http://stackoverflow.com/a/1697838/1757964
    contribution["timestamp"] = datetime.datetime(*contribution["timestamp"][:6]).isoformat()
    contributions.append(contribution)
    if(len(contributions) % 100 == 0):
        print("%d contributions read so far." % len(contributions))

with open("my-contribs.json", "w") as my_contribs:
    json.dump(contributions, my_contribs)
