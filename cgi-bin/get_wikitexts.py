import itertools
import json
import mwclient

EN_WP = "en.wikipedia.org"
USER_AGENT = "XfD Stats. Run by User:APerson. Using mwclient 0.8.1"
TITLES_PER_REQUEST = 50

def get_wikitexts(username, max_pages):
    site = mwclient.Site(EN_WP, clients_useragent=USER_AGENT)

    # Get the wikitexts of each page
    print("<p>Scanned <a href='https://en.wikipedia.org/wiki/User:{0}'>{0}</a>'s {1} most recent Wikipedia-namespace contributions.</p>".format(username, max_pages))
    contributions = get_contributions(site, username, max_pages)
    if not contributions:
        raise ValueError("No contributions for %s found." % username)
    #contributions = get_contributions_from_file(site, username)
    titles = list(set(x["title"] for x in contributions if "for deletion/" in x["title"] or "for discussion/" in x["title"]))
    if not titles:
        raise ValueError("No deletion contributions for %s found." % username)
    wikitexts = get_texts(site, titles)
    return wikitexts

def get_contributions(site, username, num_contributions):
    """Get a list of Wikipedia-namespace contributions."""
    result = []
    gen = site.usercontributions(username, namespace=4)
    for contrib in itertools.islice(gen, num_contributions):
        result.append(contrib)
    return result

def get_texts_old(site, titles):
    """Given a list of titles, get the full text of each page edited."""
    result = {}
    for title in titles:
        result[title] = site.pages[title].text()
    return result

def get_texts(site, titles):
    """Given a list of titles, get the full text of each page edited."""
    result = {}

    # ["a", "b", "c", ..., "z", "aa", "bb", ...] -> ["a|b|c|...", "z|aa|bb|..."]
    titles_strings = []
    if len(titles) > TITLES_PER_REQUEST:
        for index in xrange(0, len(titles) - 1, TITLES_PER_REQUEST):
            titles_string = ""
            for title in titles[index:min(len(titles) - 1, index + TITLES_PER_REQUEST)]:
                titles_string += title + "|"
            titles_strings.append(titles_string[:-1])
    else:
        titles_strings = ["|".join(titles)]

    for titles_string in titles_strings:
        continue_params = {"continue":""}
        while True:
            api_result = site.api("query", prop="revisions", rvprop="content", titles=titles_string, **continue_params)
            if "pages" not in api_result["query"]:
                print(api_result)
            for page_dict in api_result["query"]["pages"].values():
                result[page_dict["title"]] = page_dict["revisions"][0]["*"]
            if "continue" in api_result:
                continue_params = api_result["continue"]
            else:
                break
    return result

def get_contributions_from_file(site, username):
    """Get a list of Wikipedia-namespace contributions."""
    with open("my-contribs.json") as my_contribs_file:
        data = json.load(my_contribs_file)
        for contrib in data:
            time = datetime.datetime.strptime(contrib["timestamp"],
                                              "%Y-%m-%dT%H:%M:%S")
            contrib["timestamp"] = time.timetuple()
        return data

def get_texts_from_file(site, titles):
    """Loads a bunch of wikitexts from a file."""
    with open("my-pagetexts.json") as my_pagetexts_file:
        data = json.load(my_pagetexts_file)
        return data
