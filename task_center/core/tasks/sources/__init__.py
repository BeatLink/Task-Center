from .caldav import CaldavSource
from .database import DatabaseSource
from .decsync import DecSyncSource

SOURCES = {
    "decsync": DecSyncSource,
    "database": DatabaseSource,
    "caldav": CaldavSource
}