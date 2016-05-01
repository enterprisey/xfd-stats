import re

import utils

VOTE_TYPES = ("K", "D", "?")

def process(texts, username):
    recents = []
    for log_title, text in texts.items():
        fragments = text.split("====")[1:]
        for i in xrange(0, len(fragments), 2):
            heading, body = fragments[i:i+2]
            title = heading.replace("[[", "").replace("]]", "").replace("Template:", "").strip()
            discussion = log_title + "#" + heading.replace("[[", "").replace("]]", "").strip().replace(" ", "_")

            my_votes = list(x for x in utils.wikitext_to_votes(body) if x[1] == username)
            if not my_votes:
                continue
            vote = parse_vote(my_votes[-1][0])
            timestamp = my_votes[-1][2]

            if "The following discussion is an archived debate" in body:
                close, _ = utils.get_close(body)
            else:
                close = "Not closed yet"
            close = parse_vote(close)

            if bool(vote) and bool(close):
                recents.append((title, discussion, timestamp, vote, close))
    return recents

def get_vote(text, username):
    text = re.sub("<(s|strike|del)>.*?</(s|strike|del)>", "", text, flags=re.IGNORECASE|re.DOTALL)
    target_regex = r"^\*'''(\w+?)'''[\w,]+? [\s\S]*?\[\[User talk:" + username
    target_result = re.search(target_regex, text, flags=re.MULTILINE)
    if target_result:
        parsed = parse_vote(target_result.group(1))
        if parsed:
            return parsed
    return None

def get_close(text):
    search = re.search("The result (?:of the (?:debate|discussion) )?was(?:.*?)(?:'{3}?)(.*?)(?:'{3}?)", text, flags=re.IGNORECASE)
    if not search:
        return "?"
    else:
        return parse_vote(search.group(1))

def parse_vote(v):
    v = v.lower()
    if "comment" in v:
        return None
    elif "note" in v:
        return None
    elif "merge" in v:
        return "M"
    elif "speedy keep" in v:
	return "SK"
    elif "speedy delete" in v:
	return "SD"
    elif "keep" in v:
	return "K"
    elif "delete" in v:
	return "D"
    else:
        return None
