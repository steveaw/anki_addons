__author__ = 'Steve'
from    anki.hooks import wrap, addHook
from    aqt import mw


def set_window_title_to_anki():
    mw.setWindowTitle(u'Anki')




mw.deckBrowser.show = wrap(mw.deckBrowser.show, set_window_title_to_anki)
mw.overview.show = wrap(mw.overview.show, set_window_title_to_anki)