import re

import utils

VOTE_TYPES = ("K", "D", "M", "?")

def process(texts, username):
    recents = []
    for log_title, text in texts.items():
        fragments = text.split("====")[1:]
        for i in xrange(0, len(fragments), 2):
            heading, body = fragments[i:i+2]
            title = heading.replace("[[", "").replace("]]", "").replace("Template:", "").strip()
            discussion = log_title + "#" + heading.replace("[[", "").replace("]]", "").strip().replace(" ", "_")

            result_entry = utils.text_to_recent(body, username, parse_vote)
            if result_entry:
                timestamp, vote, close = result_entry
                if close.lower() != "relist":
                    recents.append((title, discussion, timestamp, vote, close))
    return recents

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
