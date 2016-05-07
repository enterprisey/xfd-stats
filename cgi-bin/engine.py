import cgi
import datetime
import itertools
import json
import re
import urllib

from mwclient import Site

from get_wikitexts import get_wikitexts
import afd
import tfd
import ffd
import mfd

TO_CLAUSE = re.compile(r"to \[\[.+\]\]")
NON_DISPLAYED_VOTES = ("note", "comment", "question")

def print_stats(username, max_pages):
    wikitexts = get_wikitexts(username, max_pages)

    # Sort each wikitext by category
    SUBSTRING_MAP = {"Articles": "afd", "Templates": "tfd", "Files": "ffd", "Categories": "cfd", "Redirects": "rfd", "Miscellany": "mfd"}
    PROCESS_ORDER = ("afd", "tfd", "ffd", "cfd", "rfd", "mfd")
    sorted_texts = {process: [] for process in SUBSTRING_MAP.values()}
    for title, text in wikitexts.items():
        for substring in SUBSTRING_MAP.keys():
            if title.startswith("Wikipedia:" + substring):
                sorted_texts[SUBSTRING_MAP[substring]].append((title, text))
                break

    # Used to check if sections and table cells should be displayed.
    num_pages_edited = {process: len(texts) for process, texts in sorted_texts.items()}

    # Get data for each process
    processes = {}
    for process in PROCESS_ORDER:
        if process not in globals():
            # aw man, I forgot to implement it
            processes[process] = ([], [])
            continue

        texts = sorted_texts[process]
        if not texts or len(texts) == 0:
            continue
        texts = dict(texts)

        process_module = globals()[process]
        if "process" in dir(process_module):
            recent = process_module.process(texts, username)
        else:
            recent = []

        vote_types = process_module.VOTE_TYPES
        matrix = []
        for _ in range(len(vote_types)):
            matrix.append([0] * len(vote_types))

        for _, __, ___, vote, close in recent:
            vote = process_module.parse_vote(vote)
            close = process_module.parse_vote(close)
            if bool(vote) and bool(close):
                matrix[vote_types.index(vote)][vote_types.index(close)] += 1

        processes[process] = (matrix, recent)

    print("<table id='percentages'>")
    for processes_in_this_row in (PROCESS_ORDER[:3], PROCESS_ORDER[3:]):
        print("<tr>")
        for process in processes_in_this_row:
            if num_pages_edited[process]:
                matrix, recent = processes[process]
                total_discussions = sum(sum(row) for row in matrix)
                correct_discussions = sum(matrix[i][i] for i in range(len(matrix)))
                percentage = "%.1f%%" % (100 * (float(correct_discussions) / total_discussions)) if total_discussions != 0 else "?"
                print("""  <td class='{0}'>
    <a class='percentage-link' href='#{0}'>
      <span class='process'>{1}fD</span>
      <span class='percentage'>{2}</span><br />
      {3} vote{4}<br />
      {5} page{6} edited
    </a>
  </td>""".format(process, process[0].upper(), percentage, len(recent), "" if len(recent) == 1 else "s", num_pages_edited[process], "" if num_pages_edited[process] == 1 else "s"))
            else:
                print("<td class='empty'>(No {0}fD votes)</td>".format(process[0].upper()))
        print("</tr>")
    print("</table>")

    print("<h2>Individual XfD's</h1>")
    PROCESS_NAMES = {"afd": "Articles for deletion", "tfd": "Templates for discussion", "ffd": "Files for discussion", "cfd": "Categories for discussion", "rfd": "Redirects for discussion", "mfd": "Miscellany for deletion"}
    for process in (x for x in PROCESS_ORDER if num_pages_edited[x]):
        matrix, recent = processes[process]
        print("<h3 id='%s'>%s</h3>" % (process, PROCESS_NAMES[process]))

        if process not in globals() or not recent:
            # aw man, I forgot to implement it
            print("<span class='empty-section'>(no voting data available)</span>")
            continue

        vote_types = globals()[process].VOTE_TYPES

        def make_row(row, vote_type):
            return "".join("<td class='%sagree-%szero'>%d</td>" % ("" if vote_type == result_type else "dis", "non" if vote_count > 0 else "", vote_count) for vote_count, result_type in zip(row, vote_types))
        print("<table class='matrix'>")
        print("<tr><td class='hidden'></td>" + "".join("<th>%s</th>" % v for v in vote_types) + "</tr>")
        print("".join("<tr>" + "<th>%s</th>" % vote_type + make_row(row, vote_type) + "</tr>" for vote_type, row in zip(vote_types, matrix) if vote_type != "NC"))
        print("</table>")

        print("<br />")
        print("<table class='recent'><tr><th>Page</th><th>Timestamp</th><th>Vote</th><th>Result</th></tr>")
        recent.sort(key=lambda x:x[2], reverse=True)
        recent = [x for x in recent if not any(y in x[3].lower() for y in NON_DISPLAYED_VOTES)]
        for title, discussion, timestamp, vote, close in recent:
            print("<tr><td class='title'><a href='https://en.wikipedia.org/wiki/%s'>%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (urllib.quote(discussion.encode("utf-8")), title.encode("utf-8"), datetime.datetime.strftime(timestamp, "%-d %B %Y"), format_vote_for_recent_table(vote), format_vote_for_recent_table(close)))
        print("</table><div style='clear: both;'></div>")

def format_vote_for_recent_table(vote):
    """Used to format both votes and closes for the recent tables."""
    vote = vote.encode("utf-8").capitalize()
    if "to" in vote:
        vote = vote.split("to")[0]
    return vote.replace(".", "")
