from datetime import date

__all__ = [
    'ABOUT_AUTHOR',
    'ABOUT_COPYRIGHT',
    'ABOUT_DESCRIPTION',
    'ABOUT_EMAIL',
    'ABOUT_LICENSE',
    'ABOUT_TITLE',
    'ABOUT_URL',
    'ABOUT_VERSION'
]

ABOUT_AUTHOR = 'Jessy Williams'
ABOUT_COPYRIGHT = 'Copyright %d %s' % (date.today().year, ABOUT_AUTHOR)
ABOUT_DESCRIPTION = 'An API for media database APIs which allows you to search for metadata using simple, common interface'
ABOUT_EMAIL = 'jessy@jessywilliams.com'
ABOUT_LICENSE = 'MIT'
ABOUT_TITLE = 'mapi'
ABOUT_URL = 'https://github.com/jkwill87/' + ABOUT_TITLE
ABOUT_VERSION = '0.1'
