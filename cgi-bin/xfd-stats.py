#!/usr/bin/env python

import cgitb; cgitb.enable()

import cgi
import sys

from engine import print_stats

def main():
    print_header()
    form = cgi.FieldStorage()
    username = form.getvalue("username")
    if not username:
        error_and_exit("Error! No username specified.")

    if form.getvalue("max"):
        try:
            max_pages = int(form.getvalue("max"))
        except ValueError:
            max_pages = 50
    else:
        print("Assuming that you want the most recent 50 pages.")
        max_pages = 50

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
  <a href="https://en.wikipedia.org/wiki/User:APerson" title="APerson's user page on the English Wikipedia">APerson</a> (<a href="https://en.wikipedia.org/wiki/User_talk:APerson" title="APerson's talk page on the English Wikipedia">talk!</a>) &middot; <a href="https://github.com/APerson241/xfd-stats" title="Source code on GitHub">Source code</a> &middot; <a href="https://github.com/APerson241/xfd-stats/issues" title="Issues on GitHub">Issues</a>
</footer>
</body>
</html>""")

main()
