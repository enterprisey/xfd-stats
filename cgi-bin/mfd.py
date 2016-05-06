import utils

VOTE_TYPES = ("K", "D", "SK", "SD", "NC")

def process(texts, username):
    recent = []
    for discussion, text in texts.items():
        title = discussion.replace("Wikipedia:Miscellany for deletion/", "")
        result_entry = utils.text_to_recent(text, username, parse_vote)
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
    elif "no consensus" in v:
        return "NC"
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
