import re

import utils

VOTE_TYPES = ("K", "D", "SK", "SD", "DAB", "NC")
TAG = re.compile(r"<.*?>")

def process(texts, username):
    recent = []
    for log_title, text in texts.items():
        fragments = text.split("====")[1:]
        for i in xrange(0, len(fragments), 2):
            heading, body = fragments[i:i+2]
            title = TAG.sub("", heading).strip()
            discussion = log_title + "#" + title.replace(" ", "_")

            result_entry = utils.text_to_recent(body, username, parse_vote)
            if result_entry:
                timestamp, vote, close = result_entry
                recent.append((title, discussion, timestamp, vote, close))
    return recent

def parse_vote(v):
    v = v.lower()
    if "comment" in v:
        return None
    elif "note" in v:
        return None
    elif "dab" in v:
        return "DAB"
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
