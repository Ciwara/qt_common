from database import Setup

from .updater import UpdaterInit

Setup().create_all_or_pass()
UpdaterInit()
