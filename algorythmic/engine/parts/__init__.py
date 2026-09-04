"""
Les parties instrumentales, une par couche du mixage.

@author epyidev
"""

from .bass import BassPart
from .context import PartContext
from .drums import DrumsPart
from .melody import MelodyPart
from .ostinato import OstinatoPart
from .pad import PadPart

__all__ = [
    "BassPart",
    "DrumsPart",
    "MelodyPart",
    "OstinatoPart",
    "PadPart",
    "PartContext",
]
