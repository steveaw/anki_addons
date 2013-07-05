# -*- coding: utf-8 -*-
"""
Adds the Stat Report's "Forecast Graph" to the main window's "Overview" page.

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Support: Use at your own risk. If you do find a problem please email me
or use one the following forums, however there are certain periods
throughout the year when I will not have time to do any work on
these addons.

Github page:  https://github.com/steveaw/anki_addons
Anki addons: https://groups.google.com/forum/?hl=en#!forum/anki-addons
"""
import anki.js
from aqt.overview import Overview
from anki.hooks import wrap
from anki.stats import CollectionStats
from aqt import mw


def table_adding_graph(self, _old):
    #self is overview
    ret = _old(self)
    stats = mw.col.stats()
    stats.wholeCollection = False
    report = stats.report_due_graph_only(0)
    #anki.stats.CollectionStats#_graph contains a bug in its css which
    #actually stops the graph from being displayed in the main webview
    #due to the strict doctype in use. Bug report has been submitted.
    #This is a good enough work around until the fix makes it into the release.
    report = report.replace('style="width:600; height:200;"', 'style="width:600px; height:200px;"')
    html = ret + report
    return html


def report_due_graph_only(self, type=0):
    #self is anki.stats.CollectionStats
    # 0=days, 1=weeks, 2=months
    self.type = type
    from anki.statsbg import bg

    txt = self.css % bg
    txt += self.dueGraph()
    txt += self.footer()
    # return "<script>%s\n</script><center>%s</center>" % (
    #    anki.js.jquery+anki.js.plot, txt)
    return "<script>%s\n</script><center>%s</center>" % (
        anki.js.plot, txt)


CollectionStats.report_due_graph_only = report_due_graph_only
#Needed if source fix is not present. Put hack fix in instead
#CollectionStats._graph=_graph
Overview._table = wrap(Overview._table, table_adding_graph, "around")