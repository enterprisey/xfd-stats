import datetime
import re

SIGNATURE_REGEX = r"(?:(?:\{\{unsigned.*?\}\})|(?:class=\"autosigned\")|(?:\[\[User.*?\]\].*?\(UTC\)))"
SIGNATURE = re.compile(SIGNATURE_REGEX, flags=re.IGNORECASE)
VOTE = re.compile(r"'''(.*?)'''.*?" + SIGNATURE_REGEX,
                   flags=re.IGNORECASE)
USERNAME = re.compile(r"\[\[User.*?:(.*?)(?:\||(?:\]\]))",
                  flags=re.IGNORECASE)
TIMESTAMP = re.compile(r"\d{2}:\d{2}, \d{1,2} [A-Za-z]* \d{4} \(UTC\)")
RESULT = re.compile(r"The\s+result\s+(?:of\s+the\s+(?:debate|discussion)\s+)?was(?:.*?)'''(.*?)'''.*?" + SIGNATURE_REGEX,
                    flags=re.IGNORECASE)
ARCHIVE_TEXT = "The following discussion is an archived debate"

def wikitext_to_votes(wikitext):
    """Given wikitext, returns a generator that yields votes in the form of (type, username, datetime)."""

    # Because closes are also picked up, exclude them from the results
    close = get_close(wikitext)
    if close:
        close_result, closer = close
        is_close = lambda vote, username:vote == close[0] and username == close[1]
    else:
        is_close = lambda vote, username:False

    # Find the nomination
    if close:
        nom_search_start = RESULT.search(wikitext).end(0)
    else:
        nom_search_start = 0
    nom_search_text = wikitext[nom_search_start:]
    nom_search = SIGNATURE.search(nom_search_text)
    if nom_search:
        nom_search_result = nom_search.group(0)
        username_search = USERNAME.search(nom_search_result)
        if username_search:
            nom = username_search.groups()[-1].strip()
            timestamp = get_timestamp(nom_search_result)
            yield ("Delete (Nom)", nom, timestamp)
            vote_search_start = nom_search.end(0)
        else:
            vote_search_start = 0
    else:
        vote_search_start = 0

    vote_search_text = nom_search_text[vote_search_start:]
    for each_match in VOTE.finditer(vote_search_text):
        match_text = each_match.group(0)
        vote = each_match.group(1)

        username_search = USERNAME.search(match_text)
        if username_search:
            username = username_search.groups()[-1].strip()
        else:
            username = ""

        if username and username.lower() in vote.lower():
            # For users with signatures that have bolded text
            continue

        time = get_timestamp(match_text)

        if not is_close(vote, username):
            yield (vote, username, time)

def get_timestamp(wikitext):
    """Gets the first timestamp from the given wikitext."""
    time_search = TIMESTAMP.search(wikitext)
    if time_search:
        try:
            time_string = time_search.group(0).replace("(UTC)", "").strip()
            return datetime.datetime.strptime(time_string, "%H:%M, %d %B %Y")
        except ValueError:
            return ""
    else:
        return ""

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

def text_to_recent(text, username, parse_vote=None):
    """Parses some wikitext using the provided function and returns part of a recent list entry in the form of (timestamp, vote, close)."""
    if not parse_vote:
        raise ValueError("parse_vote not provided to text_to_recent")

    my_votes = list(x for x in wikitext_to_votes(text) if x[1] == username)

    # If multiple votes are recorded, let's try to whittle it down
    if len(my_votes) > 1:
        my_votes = [x for x in my_votes if parse_vote(x[0])]

    if not my_votes:
        return None

    vote = my_votes[0][0]
    timestamp = my_votes[0][2]

    if ARCHIVE_TEXT in text:
        close_and_username = get_close(text)
        if close_and_username:
            close = close_and_username[0]
        else:
            close = "?"
    else:
        close = "Not closed yet"

    if bool(vote) and bool(close):
        return (timestamp, vote, close)


def expand_vote_abbreviation(abbreviation):
    return VOTE_ABBREVIATIONS.get(abbreviation, "?")
