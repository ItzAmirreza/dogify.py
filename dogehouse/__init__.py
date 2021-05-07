"""
DogeHouse API Wrapper
-+-+-+-+-+-+-+-+-+-+-+-
A basic wrapper for the DogeHouse API.
:copyright: (c) 2015-present Dead_Light
:license: MIT, see LICENSE for more details.

"""

__title__ = 'dogehouse'
__author__ = 'Dead_Light and VelterZi'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present Dead_Light'
__version__ = '1.0.0'

__all__ = (
    'Client', 'User', 'Room','constants'
)

from collections import namedtuple

from .core.constants import constants
from .client import Client
from .core.User import User
from .core.Room import Room

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='alpha', serial=0)