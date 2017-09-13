|licence| |pypi| |travis_ci| |api|


mapi
====

mapi (**M**\ etadata **API**) is a python library which provides a high-level interface for media database providers, allowing users to efficiently search for television and movie metadata using a simple interface.


Installation
============

`$ pip install mapi`


Examples
========

Searching for a television show by series using TVDb
----------------------------------------------------

Here is a fairly straight forward example, say we just want to get a listing of episodes from
Rick and Morty season 2:

>>> from mapi.providers import TVDb
>>> client = TVDb()  # API Key taken from environment variables
>>> results = client.search(series='Rick and Morty', season=2)
>>> for result in results:
>>>     print(result)
Rick and Morty - 02x01 - A Rickle in Time
Rick and Morty - 02x02 - Mortynight Run
Rick and Morty - 02x03 - Auto Erotic Assimilation
Rick and Morty - 02x04 - Total Rickall
Rick and Morty - 02x05 - Get Schwifty
Rick and Morty - 02x06 - The Ricks Must Be Crazy
Rick and Morty - 02x07 - Big Trouble in Little Sanchez
Rick and Morty - 02x08 - Interdimensional Cable 2: Tempting Fate
Rick and Morty - 02x09 - Look Who's Purging Now
Rick and Morty - 02x10 - The Wedding Squanchers

Mapi searches yield Metadata objects, which themselves are just MutableMappings which can be treated like regular old Python dictionaries. That being said, they overwrite `__str__` so that they get prettily printed as seen above. This can easily be overridden, however. Say we would rather use a SxxExx format:

>>> from mapi.providers import TVDb
>>> client = TVDb()  # API Key taken from environment variables
>>> result = client.search(series='Adventure Time', season=5, episode=3)
>>> print(next(result).format('<$series - >< - S$season><E$episode - >< - $title>'))
Adventure Time - S05E03 - Five More Short Graybles


You can read more about the `format` method in the source documentation.


Searching for a movie by title and year using IMDb
--------------------------------------------------

Okay, so no we want to look up some movies. We can search for using a specific year, by an upper range using '-year', by a lower range using 'year-', or between a range of years using 'year-year'. Lets use the latter to get a listing of Star Trek movies from the 90s. As it turns out, there's a lot.

>>> from mapi.providers import IMDb
>>> client = IMDb()
>>> results = client.search(title='Star Trek', year='1990-1999')
>>> for i, result in enumerate(results, 1):
>>>     print('%d) %s' % (i, result))
>>>     if i > 9: break
1) Star Trek: Voyager (1995)
2) Star Trek: First Contact (1996)
3) Star Trek VI: The Undiscovered Country (1991)
4) Star Trek: Generations (1994)
5) Star Trek: Insurrection (1998)
6) Star Trek: The Experience - The Klingon Encounter (1998)
7) Journey's End: The Saga of Star Trek - The Next Generation (1994)
8) Star Trek: 30 Years and Beyond (1996)
9) Ultimate Trek: Star Trek's Greatest Moments (1999)
10) Star Trek: A Captain's Log (1994)

Searches return a generator, so by breaking on 10, we only ask for what we need, reducing the bandwidth and time required for the request.


Looking up by ID
----------------

If you just want to lookup metadata using an API Provider's ID code, you can do that too:

>>> from pprint import pprint
>>> from mapi.providers import TMDb
>>> client = TMDb()
>>> results = client.search(id_tmdb=9340)  # Using TMDb ID
>>> pprint(dict(next(results)))
{'date': '1985-06-06',
 'id_tmdb': '9340',
 'media': 'movie',
 'synopsis': 'A young teenager named Mikey Walsh finds an old treasure map in '
             "his father's attic. Hoping to save their homes from demolition, "
             'Mikey and his friends Data Wang, Chunk Cohen, and Mouth '
             'Devereaux run off on a big quest to find the secret stash of '
             'Pirate One-Eyed Willie.',
 'title': 'The Goonies'}

Some APIs, like TMDb, allow you to search by an IMDb 'tt-const' as well:

>>> results = client.search(id_imdb='tt0089218')  # Using IMDb ID
>>> pprint(dict(next(results)))
{'date': '1985-06-06',
 'id_tmdb': 9340,
 'media': 'movie',
 'synopsis': 'A young teenager named Mikey Walsh finds an old treasure map in '
             "his father's attic. Hoping to save their homes from demolition, "
             'Mikey and his friends Data Wang, Chunk Cohen, and Mouth '
             'Devereaux run off on a big quest to find the secret stash of '
             'Pirate One-Eyed Willie.',
 'title': 'The Goonies'}


Handling a search gone awry
---------------------------

Not all searches yield results; maybe you had a typo, maybe the data just isn't there, either way 
theres no need to fret, this can be handled gracefully using exception handling:

>>> from mapi.providers import TMDb
>>> client = TMDb()
>>> try:
>>>     print(next(client.search(id_imdb='invalid_id')))
>>> except MapiNotFoundException:
>>>     print('Nothing found :(')
None found :(


Usage Details
=============

Provider Configuration
----------------------

- TVDb and TMDb require an API key to successfully be initialized
- These can be provided using environment variables; API_KEY_TMDB and API_KEY_TVDB, respectively
- These can also be provided as `api_key`, a parameter to the provider classes.


Searching
---------

The following table describes the permissible fields which may be used for a
given search query. Extra fields are simply ignored.

+----------+---------------------+-----------+------------------------+----------------------------+
| Field    | API                 | Type      | Description            | Notes                      |
+==========+=====================+===========+========================+============================+
| id_imdb  | IMDb, TMDb, TVDb    | str       | IMDb movie id key      | [1]_ [2]_                  |
+----------+---------------------+-----------+------------------------+----------------------------+
| id_tmdb  | TMDb                | str / int | TMDb movie id key      | [2]_ [3]_                  |
+----------+---------------------+-----------+------------------------+----------------------------+
| id_tvdb  | TVDb series id key  | str / int | TVDb season id key     | [2]_ [3]_                  |
+----------+---------------------+-----------+------------------------+----------------------------+
| title    | IMDb, TMDb          | str       | Feature's title        |                            |
+----------+---------------------+-----------+------------------------+----------------------------+
| year     | IMDb, TMDb          | str / int | Feature's release year |                            |
+----------+---------------------+-----------+------------------------+----------------------------+
| series   | TVDb                | str       | Series' name           |                            |
+----------+---------------------+-----------+------------------------+----------------------------+
| season   | TVDb                | str / int | Series' airing season  |                            |
+----------+---------------------+-----------+------------------------+----------------------------+
| episode  | TVDb                | str / int | Series' airing episode | [3]_                       |
+----------+---------------------+-----------+------------------------+----------------------------+


Results
-------

Each provider is guaranteed to return the following fields for a successful
search as strings. Notice that they are largely the fields as the search
parameters-- in fact, you can even next search calls within each other if you
so desire.

+----------+------------+--------------------------------------------------------------------------+
| Field    | API        | Description                                                              |
+==========+============+==========================================================================+
| id_imdb  | IMDb       | IMDb movie id key                                                        |
+----------+------------+--------------------------------------------------------------------------+
| id_tmdb  | TMDb       | TMDb movie id key                                                        |
+----------+------------+--------------------------------------------------------------------------+
| id_tvdb  | TVDb       | TVDb season id key                                                       |
+----------+------------+--------------------------------------------------------------------------+
| title    | IMDb, TMDb | Feature's title                                                          |
+----------+------------+--------------------------------------------------------------------------+
| date     | ALL        | Media's release date (YYYY-MM-DD)                                        |
+----------+------------+--------------------------------------------------------------------------+
| synopsis | ALL        | Media synopsis                                                           |
+----------+------------+--------------------------------------------------------------------------+
| media    | ALL        | Media type; either 'movie' or 'television'                               |
+----------+------------+--------------------------------------------------------------------------+
| series   | TVDb       | Series' name                                                             |
+----------+------------+--------------------------------------------------------------------------+
| season   | TVDb       | Series' airing season                                                    |
+----------+------------+--------------------------------------------------------------------------+
| episode  | TVDb       | Series' airing episode                                                   |
+----------+------------+--------------------------------------------------------------------------+


License
=======

MIT. See license.txt for details.


Notes
=====
.. [1] id_imdb must be prefixed with 'tt'.
.. [2] Although ID, title, and series are each optional, movie queries must have
       either an ID or title to yield any results, and television queries must
       have either and ID or series to yield any results.
.. [3] If this field is passed as a string it must be numeric.

.. |licence| image:: https://img.shields.io/github/license/jkwill87/mapi.svg
   :target: https://en.wikipedia.org/wiki/MIT_License
.. |travis_ci| image:: https://img.shields.io/travis/jkwill87/mapi/develop.svg
   :target: https://travis-ci.org/jkwill87/mapi
.. |pypi| image:: https://img.shields.io/pypi/v/mapi.svg
   :target: https://pypi.python.org/pypi/mapi
.. |api| image:: https://img.shields.io/badge/api-IMDb/TMDb/TVDb-D8D200.svg
