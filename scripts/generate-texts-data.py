import json
import pywikibot

from clint.textui import progress

site = pywikibot.Site("en", "wikipedia")
site.login()

with open("my-contribs.json", "r") as my_contribs_file:
    data = json.load(my_contribs_file)
titles = list(set(x["title"] for x in data
                  if ("Articles for deletion/" in x["title"] or
                      "for discussion/" in x["title"])))

# SLICE TITLES
titles = titles[:200]

result = {}
for title in progress.bar(titles):
    page = pywikibot.Page(site, title)

    if page.isRedirectPage():
        continue

    result[title] = page.get()

with open("my-pagetexts.json", "w") as my_pagetexts_file:
    json.dump(result, my_pagetexts_file)
