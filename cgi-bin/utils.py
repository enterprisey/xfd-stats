import datetime
import re

SIGNATURE = r"(?:(?:\{\{unsigned.*?\}\})|(?:class=\"autosigned\")|(?:\[\[User.*?\]\].*?\(UTC\)))"
VOTE = re.compile(r"'''(.*?)'''.*?" + SIGNATURE,
                   flags=re.IGNORECASE)
USERNAME = re.compile(r"\[\[User.*?:(.*?)(?:\||(?:\]\]))",
                  flags=re.IGNORECASE)
TIMESTAMP = re.compile(r"\d{2}:\d{2}, \d{1,2} [A-Za-z]* \d{4} \(UTC\)")
RESULT = re.compile(r"The\s+result\s+(?:of\s+the\s+(?:debate|discussion)\s+)?was(?:.*?)'''(.*?)'''.*?" + SIGNATURE,
                    flags=re.IGNORECASE)

def wikitext_to_votes(wikitext):
    """Given wikitext, returns a generator that yields votes in the form of (type, username, datetime)."""

    # Because closes are also picked up, exclude them from the results
    close = get_close(wikitext)
    if close:
        close_result, closer = close
        is_close = lambda vote, username:vote == close_result and username == closer
    else:
        is_close = lambda vote, username:False

    for each_match in VOTE.finditer(wikitext):
        match_text = each_match.group(0)
        vote = each_match.group(1)

        username_search = USERNAME.search(match_text)
        if username_search:
            username = username_search.group(1).strip()
        else:
            username = ""

        time_search = TIMESTAMP.search(match_text)
        if time_search:
            try:
                time_string = time_search.group(0).replace("(UTC)", "").strip()
                time = datetime.datetime.strptime(time_string, "%H:%M, %d %B %Y")
            except ValueError:
                time = ""
        else:
            time = ""

        if not is_close(vote, username):
            yield (vote, username, time)

def get_close(wikitext):
    """Returns a tuple in the form of (result, username), where username is the closer."""
    result_search = RESULT.search(wikitext)
    if not result_search:
        return None
    username_search = USERNAME.search(result_search.group(0))
    if username_search:
        username = username_search.group(1).strip()
    else:
        username = ""
    return result_search.group(1), username
