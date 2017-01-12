#!/usr/bin/env python

import cgitb; cgitb.enable()

import cgi
import sys

from engine import print_stats

DEFAULT_MAX_PAGES = 50
MAXIMUM_MAX_PAGES = 10000

def main():
    print_header()
    form = cgi.FieldStorage()
    username = form.getvalue("username")
    if not username:
        error_and_exit("Error! No username specified.")

    if form.getvalue("max"):
        try:
            max_pages = min(int(form.getvalue("max")), MAXIMUM_MAX_PAGES)
        except ValueError:
            max_pages = DEFAULT_MAX_PAGES
    else:
        print("Assuming that you want the most recent 50 pages.")
        max_pages = DEFAULT_MAX_PAGES

    print("""<h1>XfD Stats for %s</h1><div id="stats">""" % username)
    try:
        print_stats(username, max_pages)
    except ValueError as e:
        error_and_exit("Error! Unable to calculate statistics. " + str(e) + " You may have misspelled that username.")
    print("</div>")
    print_footer()

def print_header():
    print("Content-Type: text/html")
    print
    print("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>XfD Stats Results</title>
    <link href="../assets/css/style.css" rel="stylesheet" />
    <link href="../assets/css/results.css" rel="stylesheet" />
    </head>
    <body><p><a href="../index.html">&larr; New search</a></p>""")

def error_and_exit(error):
    print("""<p class="error">%s</p>""" % error)
    print_footer()
    sys.exit(0)

def print_footer():
    print("""
<p><a href="../index.html">&larr; New search</a></p>
<footer>
  <a href="https://en.wikipedia.org/wiki/User:Enterprisey" title="Enterprisey's user page on the English Wikipedia">Enterprisey</a> (<a href="https://en.wikipedia.org/wiki/User_talk:Enterprisey" title="Enterprisey's talk page on the English Wikipedia">talk!</a>) &middot; <a href="https://github.com/APerson241/xfd-stats" title="Source code on GitHub">Source code</a> &middot; <a href="https://github.com/APerson241/xfd-stats/issues" title="Issues on GitHub">Issues</a>
</footer>
</body>
</html>""")

main()
