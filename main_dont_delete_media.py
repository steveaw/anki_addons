import os
import datetime
import shutil
from anki.lang import _
from aqt.main import AnkiQt
from aqt.utils import askUser, tooltip, showWarning

__author__ = 'Steve'

def deleteUnused(self, unused, diag):
    if not askUser(
        _("Move unused media to the 'Deleted media' folder?")):
        return
    base_del_dir = self.pm._ensureExists(
            os.path.join(self.pm.profileFolder(), "deleted_media"))
    dest_del_dir = os.path.join(base_del_dir , 'deleted%s' % (datetime.datetime.now().strftime("%y%m%d_%H%M%S")))
    if  os.path.exists(dest_del_dir):
        showWarning('Folder already exists')
        return
    os.makedirs(dest_del_dir)
    mdir = self.col.media.dir()
    for f in unused:
        source_path = os.path.join(mdir, f)
        target_path = os.path.join(dest_del_dir, f)
        shutil.move(source_path,target_path )
    tooltip(_("Deleted."))
    diag.close()



AnkiQt.deleteUnused=deleteUnused