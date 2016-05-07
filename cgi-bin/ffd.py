import utils

VOTE_TYPES = ("K", "D", "SOD", "SK", "SD", "?")

def process(texts, username):
    recents = []
    for log_title, text in texts.items():
        fragments = text.split("====")[1:]
        recent_produced = False
        for i in xrange(0, len(fragments), 2):
            heading, body = fragments[i:i+2]
            title = heading.replace("[[", "").replace("]]", "").replace(":File:", "").strip()
            discussion = log_title + "#" + heading.replace("[[:", "").replace("]]", "").strip().replace(" ", "_")

            # Remove everything but the discussion
            end_of_metadata = body.find("upload log]]")
            metadata = body[:end_of_metadata]
            body = body[end_of_metadata:]

            nominator_search = utils.USERNAME.search(body)
            if nominator_search:
                nominator = nominator_search.group(1).strip()
                if username == nominator:
                    close_and_username = utils.get_close(metadata)
                    if close_and_username:
                        close = close_and_username[0]
                    else:
                        close = "Not closed yet"

                    timestamp = utils.get_timestamp(body)

                    recents.append((title, discussion, timestamp, "Delete (Nom)", close))
                    continue
            else:
                continue

            result_entry = utils.text_to_recent(body, username, parse_vote)
            if result_entry:
                timestamp, vote, close = result_entry
                recents.append((title, discussion, timestamp, vote, close))
    return recents

def parse_vote(v):
    v = v.lower()
    if "comment" in v:
        return None
    elif "note" in v:
        return None
    elif "soft delete" in v:
        return "SOD"
    elif "speedy keep" in v:
	return "SK"
    elif "speedy delete" in v:
	return "SD"
    elif "keep" in v or "kept" in v:
	return "K"
    elif "delete" in v:
	return "D"
    else:
        return None
