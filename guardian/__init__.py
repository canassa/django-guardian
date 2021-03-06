"""
Implementation of per object permissions for Django 1.2.
"""
import listeners

VERSION = (0, 1, 0, 'beta')

__version__ = '.'.join((str(each) for each in VERSION[:4]))

def get_version():
    """
    Returns shorter version (digit parts only) as string.
    """
    return '.'.join((str(each) for each in VERSION[:3]))

