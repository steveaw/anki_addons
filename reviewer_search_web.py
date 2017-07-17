# -*- coding: utf-8 -*-
"""
Adds Search For Selected Text to the Reviewer Window's context/popup menu

https://ankiweb.net/shared/info/798922495

Copyright: Steve AW <steveawa@gmail.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Note: AnkiWebView.contextMenuEvent is replaced, but only to add a hook
which should make it easy to maintain.

Support: Use at your own risk. If you do find a problem please email me
or use one the following forums, however there are certain periods
throughout the year when I will not have time to do any work on
these addons.

Github page:  https://github.com/steveaw/anki_addons
Anki addons: https://groups.google.com/forum/?hl=en#!forum/anki-addons
"""

providers = [
    ['Google Images', 'https://www.google.com/search?tbm=isch&q=%s'],
    ['Wikipedia', 'http://en.wikipedia.org/wiki/wiki.html?search=%s'],
    ['Wiktionary', 'https://en.wiktionary.org/wiki/%s']
]

from aqt.webview import AnkiWebView
from aqt.qt import *
from aqt.utils import tooltip
from anki.hooks import runHook, addHook
import urllib


def selected_text_as_query(web_view):
    sel = web_view.page().selectedText()
    return " ".join(sel.split())


def on_search_for_selection(web_view, search_url):
    sel_encode = selected_text_as_query(web_view).encode('utf8', 'ignore')
    #need to do this the long way around to avoid double % encoding
    url = QUrl.fromEncoded(SEARCH_URL % urllib.quote(sel_encode))
    #openLink(search_url + sel_encode)
    tooltip(_("Loading..."), period=1000)
    QDesktopServices.openUrl(url)


def contextMenuEvent(self, evt):
    # lazy: only run in reviewer
    import aqt

    if aqt.mw.state != "review":
        return
    m = QMenu(self)
    a = m.addAction(_("Copy"))
    a.connect(a, SIGNAL("triggered()"),
              lambda: self.triggerPageAction(QWebPage.Copy))
    #Only change is the following statement
    runHook("AnkiWebView.contextMenuEvent", self, m)
    m.popup(QCursor.pos())


def menu_action_factory(provider):
    def insert_search_menu_action(anki_web_view, m):
        selected = selected_text_as_query(anki_web_view)
        truncated = (selected[:40] + '..') if len(selected) > 40 else selected
        a = m.addAction('Search %s For "%s" ' % (provider[0], truncated))
        a.connect(a, SIGNAL("triggered()"),
                  lambda wv=anki_web_view: on_search_for_selection(wv, provider[1]))

    return insert_search_menu_action


#AnkiWebView.contextMenuEvent = contextMenuEvent
for provider in providers:
    addHook("AnkiWebView.contextMenuEvent", menu_action_factory(provider))
