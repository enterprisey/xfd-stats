import cgi
import re

import utils

VOTE_TYPES = ("K", "D", "SK", "SD", "M", "R", "T", "U", "?")

def process(texts, username):
    recent = []
    for discussion, text in texts.items():
        title = discussion.replace("Wikipedia:Articles for deletion/", "")

        my_votes = list(x for x in utils.wikitext_to_votes(text) if x[1] == username)
        if not my_votes:
            continue
        vote = parse_vote(my_votes[-1][0])
        timestamp = my_votes[-1][2]

        if "The following discussion is an archived debate" in text:
            close, _ = utils.get_close(text)
        else:
            close = "Not closed yet"
        close = parse_vote(close)

        if bool(vote) and bool(close):
            recent.append((title, discussion, timestamp, vote, close))
    return recent

def parse_vote(v):
    v = v.lower()
    if "comment" in v:
	return None
    elif "note" in v:
	return None
    elif "merge" in v:
	return "M"
    elif "redirect" in v:
	return "R"
    elif "speedy keep" in v:
	return "SK"
    elif "speedy delete" in v:
	return "SD"
    elif "keep" in v:
	return "K"
    elif "delete" in v:
	return "D"
    elif "transwiki" in v:
	return "T"
    elif ("userfy" in v) or ("userfied" in v) or ("incubat" in v):
	return "U"
    else:
	return None