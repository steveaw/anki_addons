# -*- coding: utf-8 -*-
# Based on CardStats which is copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
from itertools import tee, izip
import time
from datetime import datetime
import json
from PyQt4.QtCore import Qt, QSize, SIGNAL, QObject, QTimer

from PyQt4.QtGui import QDockWidget, QAction, QVBoxLayout
from PyQt4.QtWebKit import QWebView

from anki.hooks import addHook, wrap
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView
import anki.js

END_HOUR = 13

START_HOUR = 6


class ReviewerDockWidget(QObject):
    def __init__(self, mw):
        QObject.__init__(self)
        self.mw = mw
        self.shown = False
        self.ss_timer = None
        # addHook("showQuestion", self._update)
        # addHook("deckClosing", self.hide)
        # addHook("reviewCleanup", self.hide)

    def _addDockable(self, title, w):
        dock = QDockWidget(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetVerticalTitleBar)
        dock.setWidget(w)
        #todo: figure out what the left and top margin are
        #todo: get resize events and update content
        # w.setStyleSheet(" background-color: #FF0000;")
        # dock.setStyleSheet(" background-color: #00FF00;")
        # dock.layout().setContentsMargins(10,0,0,0)
        mw.addDockWidget(Qt.BottomDockWidgetArea, dock)
        return dock

    def _remDockable(self, dock):
        mw.removeDockWidget(dock)

    def show(self):
        if not self.shown:
            self.web = QWebView()
            self.shown = self._addDockable("Chart", self.web)
            self.shown.connect(self.shown, SIGNAL("visibilityChanged(bool)"),
                               self._visChange)
        self._update()

    def hide(self):
        if self.shown:
            self._remDockable(self.shown)
            self.shown = None


    def toggle(self):
        if self.shown:
            self.hide()
        else:
            self.show()

    def _visChange(self, vis):
        if not vis:
            # schedule removal for after evt has finished
            self.mw.progress.timer(100, self.hide, False)

    def _update_timer(self):
        #sent by update timer
        print("%s _Update_timer" % (datetime.now().strftime("%y%m%d_%H%M%S")))
        self.ss_timer = None
        self._update()

    def _update(self, last_ease=None):
        # print("%s _Update" % (datetime.now().strftime("%y%m%d_%H%M%S")))
        if self.ss_timer:
            timer = self.ss_timer
            self.ss_timer = None
            timer.stop()

        if not self.shown:
            return

        contents = DailyReviewChartModel(last_ease=last_ease).html_contents()
        contents
        # print("%s Setting contents" % (datetime.now().strftime("%y%m%d_%H%M%S")))
        self.web.setHtml(contents)
        if not self.ss_timer:
            # self.ss_timer = QTimer.singleShot(15000, self._update_timer)
            self.ss_timer = QTimer()
            self.ss_timer.setSingleShot(True)
            self.ss_timer.timeout.connect(self._update_timer)
            self.ss_timer.start(15000)


dock = ReviewerDockWidget(mw)


class RevLogEntry(object):
    def __init__(self, secs_offset, ease, did, card_type):
        #start_offset is seconds past day_start_offset (which always appears to be midnight)
        self.secs_offset = secs_offset
        self.ease = ease
        self.did = did
        self.card_type = card_type

    def is_new_card(self):
        return self.card_type == 0


class DailyReviewChartModel(QObject):
    def __init__(self, last_ease=None):
        """

        """
        QObject.__init__(self)
        self.last_ease = last_ease
        self.entries = None
        self.today_start_id = None
        if mw.col:
            self.today_start_id = (mw.col.sched.dayCutoff - 86400) * 1000
            raw_entries = mw.col.db.all(
                " SELECT revlog.id, revlog.ease, cards.did, revlog.type FROM revlog JOIN cards ON revlog.cid=cards.id WHERE revlog.id > %s ORDER BY revlog.id" % self.today_start_id)

            self.entries = [RevLogEntry(int((each[0] - self.today_start_id) // 1000), each[1], each[2], each[3]) for each
                            in
                            raw_entries]
            if self.entries:
                self.first_secs_offset = self.entries[0].secs_offset
                self.last_secs_offset = self.entries[-1].secs_offset
            else:
                #put in reasonable defaults
                self.first_secs_offset = START_HOUR * 60 * 60
                self.last_secs_offset = END_HOUR * 60 * 60
            #Always show at min from 6-1PM
            self.start_offset_hour = min((self.first_secs_offset) // 3600, START_HOUR)
            self.end_offset_hour = max(((self.last_secs_offset + 15 * 60 ) // 3600 + 1), END_HOUR)
            assert (self.end_offset_hour <= 24)

    def calc_plot_index(self, offset):
        return (offset - (self.start_offset_hour * 3600)) // 120


    def html_contents(self):

    #todo: second div showing rating/ "Answer Confirmation" etc?
    #todo: Smaller/closer xaxis font

    #todo: backcolor ... Designer?
    #todo: colors for different decks/new cards.
    #todo: try latest version
    # or just a vetical line when a desk switch is detected?
    # blue for new cards
        #todo: red dots for fails?
        BAR_HEIGHT = 8

        #if not self.entries: return ""
        if not mw.col: return ""
        plot_size = int(( self.end_offset_hour - self.start_offset_hour + 1) * (3600 // 120))
        plot_non_new = [0] * plot_size
        plot_new = [0] * plot_size

        for entry in self.entries:
            plot_index = self.calc_plot_index(entry.secs_offset)
            if entry.is_new_card():
                plot_new[plot_index] += 1
            else:
                plot_non_new[plot_index] += 1

        #todo: set the max plot count to be bar-height -1 so can always see deck cahnges?
        data_non_new = [[i, count] for (i, count) in enumerate(plot_non_new) if count > 0]
        data_new = [[i, count] for (i, count) in enumerate(plot_new) if count > 0]


        def pairwise(iterable):
            "s -> (s0,s1), (s1,s2), (s2, s3), ..."
            a, b = tee(iterable)
            next(b, None)
            return izip(a, b)

        did_change_set = {self.calc_plot_index(e2.secs_offset) for e1, e2 in pairwise(self.entries) if
                          not e1.did == e2.did}
        did_change_set.add(self.calc_plot_index(self.first_secs_offset))
        did_change_set.add(self.calc_plot_index(self.last_secs_offset) + 1)
        #get rid of changes directly next to each other
        #did_change_set_reduced = {x * 2 for x in {x // 2 for x in did_change_set}}
        did_change_set_reduced =   did_change_set
        did_changes = sorted(did_change_set_reduced)

        grid_val = dict(markings=[])
        mark_color = "rgba(0, 0, 0, 0.07)"
        for did_change1, did_change2 in pairwise(did_changes):
            mark_color = "rgba(0, 0, 0, 0.1)" if mark_color == "rgba(0, 0, 0, 0.3)" else "rgba(0, 0, 0, 0.3)"
            grid_val["markings"].append(
                dict(xaxis={"from": did_change1,
                            "to": did_change2},
                     color=mark_color, lineWidth=1))


        #Add red column
        self.secs_since_last = int(time.time() - (self.today_start_id / 1000))
        if self.secs_since_last > (self.last_secs_offset + 35):
            grid_val["markings"].append(
                dict(xaxis={"from": self.calc_plot_index(self.last_secs_offset),
                            "to": max((self.calc_plot_index(self.secs_since_last) + 1),
                                      (self.calc_plot_index(self.last_secs_offset) + 1))},
                     color="rgba(255, 0, 0, 0.7)", lineWidth=1))


        def am_pm_string(hour):
            return ('%sAM' % hour) if hour <= 12 else ('%sPM' % (hour - 12))

        ticks = [[(hour_num - self.start_offset_hour) * 3600 // 120, am_pm_string(hour_num)]
                 for hour_num in range(self.start_offset_hour, self.end_offset_hour + 1)]
        xaxis_val = dict(ticks=ticks, min=ticks[0][0], max=ticks[-1][0])

        non_new_series_val = dict(stack=0, data=data_non_new, bars=dict(show=True, fillColor="#008800", lineWidth=1),
                                  color="#000000")
        new_series_val = dict(stack=0, data=data_new, bars=dict(show=True, fillColor="4F80FF", lineWidth=1),
                              color="#000000")

        js_values = dict(p1=json.dumps([non_new_series_val, new_series_val]),
                         other=json.dumps(dict(xaxis=xaxis_val,
                                               yaxis=dict(min=0, max=BAR_HEIGHT, ticks=[[0, "0"], [5, "5"]]),
                                               grid=grid_val
                         )))
        #todo: hack test
        count = list(mw.col.sched.counts(mw.reviewer.card))[2] if mw.state == "review" else "na"

        floater_html = """
        Ease: %s<br>
        <div style="font-size:20px;color:#007700"> %s</div>
        """ % (self.last_ease , count)



        inner_script = """
<script type="text/javascript">
	$(function() {
 		$.plot("#placeholder", %(p1)s , %(other)s);});
</script>  """ % js_values

        div_html = """
<div id="content">
		<div class="demo-container">
		<div id="floater">%s</div>
			<div id="placeholder" class="demo-placeholder"></div>
		</div>
</div> """ % floater_html

        return "<html>%s<body>%s</body></html>" % (self.html_style_and_script(), inner_script + div_html)

    def html_style_and_script(self):
        css = """
        html, body, div { margin: 0; border: 0 none; padding: 0; background-color:#DEDEDE;}
html, body,  { height: 100%; min-height: 100%; }

#floater {
    float:left;
    width:95px;
}

.demo-container {
	box-sizing: border-box;

	height: 100%;
	padding: 0px 0px 0px 0px;
	margin: 0px 0px 0px 0px;
	border: 1px solid #ddd;

}

.demo-placeholder {
	width: auto;
    margin-left: 100px;
	height: 100%;
	font-size: 14px;
	line-height: 0.8em;
	overflow:hidden;}
	"""
        return """
<head>
<style>
%s
</style>
<script>%s
</script>
</head>""" % (css, anki.js.jquery + anki.js.plot)


def toggle_chart_dock(on):
    dock.toggle()
    #will stop the timer if not shown
    dock._update()


# def updateDockNow():
#     dock._update()


def answer_card_updating_graph(self, ease):
    dock._update(last_ease=ease)

def reviewer_show(self):
    dock._update()

def profile_loaded_hook():
    dock._update()



toggle_chart_dock(True)

action = QAction(mw)
action.setText("Review Chart")
action.setCheckable(True)
mw.form.menuTools.addAction(action)
#todo: fix this
mw.connect(action, SIGNAL("toggled(bool)"), toggle_chart_dock)



addHook("profileLoaded",profile_loaded_hook)
Reviewer._answerCard = wrap(Reviewer._answerCard, answer_card_updating_graph, "after")
Reviewer.show	=	wrap(Reviewer.show,	reviewer_show)