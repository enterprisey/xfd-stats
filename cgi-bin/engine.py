import cgi
import datetime
import itertools
import json

from mwclient import Site

from get_wikitexts import get_wikitexts
import afd
import tfd
import mfd

# These next few imports are just so we can screw with globals()
from afd import process as process_afd
from tfd import process as process_tfd
from mfd import process as process_mfd

def print_stats(username, max_pages):
    wikitexts = get_wikitexts(username, max_pages)

    # Sort each wikitext by category
    SUBSTRING_MAP = {"Articles": "afd", "Templates": "tfd", "Files": "ffd", "Categories": "cfd", "Redirects": "rfd", "Miscellany": "mfd"}
    sorted_texts = {process: [] for process in SUBSTRING_MAP.values()}
    for title, text in wikitexts.items():
        for substring in SUBSTRING_MAP.keys():
            if title.startswith("Wikipedia:" + substring):
                sorted_texts[SUBSTRING_MAP[substring]].append((title, text))
                break

    # Remove processes with no wikitexts
    sorted_texts = {x: dict(y) for x, y in sorted_texts.items() if y}

    print("<table><tr><th>Process</th><th>Number of unique pages edited</th></tr>")
    print("".join("<tr><td>%s</td><td>%d</td></tr>" % (process[0].upper() + "fD", len(texts)) for process, texts in sorted_texts.items()))
    print("</table>")

    # Get data for each process
    processes = []
    for process, texts in sorted_texts.items():
        if process not in globals():
            # aw man, I forgot to implement it
            processes.append((process, [], []))
            continue

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
            if vote not in vote_types: continue
            if close not in vote_types: continue
            matrix[vote_types.index(vote)][vote_types.index(close)] += 1

        processes.append((process, matrix, recent))

    process_matrix_recent = zip(sorted_texts.keys(), zip(*processes)[1], zip(*processes)[2])

    print("<div id='percentages'>")
    percentage_wrapper_width = ((100 - 11 * (len(sorted_texts) - 1)) / len(sorted_texts))
    for process, matrix, recent in process_matrix_recent:
        if process not in globals():
            # aw man, I forgot to implement it
            percentage = "?"
        else:
            total_discussions = sum(sum(row) for row in matrix)
            correct_discussions = sum(matrix[i][i] for i in range(len(matrix)))
            percentage = "%.1f%%" % (100 * (float(correct_discussions) / total_discussions)) if total_discussions != 0 else "?"

        print("<a class='percentage-wrapper %s' style='width: %d%%;' href='#%s'><span class='process'>%sfD</span><span class='percentage'>%s</span><br />%d vote%s</a>" % (process, percentage_wrapper_width, process, process[0].upper(), percentage, len(recent), "" if len(recent) == 1 else "s"))
    print("</div>")

    print("<h2>Individual XfD's</h1>")
    PROCESS_NAMES = {"afd": "Articles for deletion", "tfd": "Templates for discussion", "ffd": "Files for discussion", "cfd": "Categories for discussion", "rfd": "Redirects for discussion", "mfd": "Miscellany for deletion"}
    for process, matrix, recent in process_matrix_recent:
        print("<h3 id='%s'>%s</h3>" % (process, PROCESS_NAMES[process]))

        if process not in globals():
            # aw man, I forgot to implement it
            print("(no data available)")
            continue

        vote_types = globals()[process].VOTE_TYPES
        print("<table class='matrix'>")
        print("<tr><td></td>" + "".join("<th>%s</th>" % v for v in vote_types) + "</tr>")
        print("".join("<tr>" + "<th>%s</th>" % vote_type + "".join("<td class='%sagree-%szero'>%d</td>" % ("" if vote_type == result_type else "dis", "non" if x > 0 else "", x) for x, result_type in zip(row, vote_types)) + "</tr>" for vote_type, row in zip(vote_types, matrix)))
        print("</table>")

        if recent:
            print("<br />")
            print("<table><tr><th>Page</th><th>Timestamp</th><th>Vote</th><th>Result</th></tr>")
            recent.sort(key=lambda x:x[2], reverse=True)
            for title, discussion, timestamp, vote, close in recent:
                print("<tr><td><a href='https://en.wikipedia.org/wiki/%s'>%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (discussion.encode("utf-8"), title.encode("utf-8"), datetime.datetime.strftime(timestamp, "%-d %B %Y"), vote, close))
            print("</table>")
        else:
            print("<span class='recent'>(no recent votes)</span>")

        print("<div style='clear: both;'></div>")
