|licence| |pypi| |travis_ci| |api|


mapi
====

mapi (**M**\ etadata **API**) is a python library which provides a high-level interface for media database providers, allowing users to search for television and movie metadata using a simple interface. Supports and tested against Python 2.7, Python 3, and PyPy3.


Examples
========

Searching for a television show by series using TVDb
----------------------------------------------------

>>> from pprint import pprint
>>> from mapi.providers import TVDb
>>> client = TVDb(max_hits=3)
>>> hits = client.search(series='Rick and Morty', season=2)
>>> pprint(hit)
[{'episode': '1',
  'id_tvdb': '275274',
  'media': 'television',
  'season': '2',
  'series': 'Rick and Morty',
  'synopsis': 'Rick, Morty, and Summer get into trouble when time is fractured '
              'by a feedback loop of uncertainty that split reality into more '
              'than one equally possible impossibilities. Meanwhile, Beth and '
              'Jerry go to extreme lengths to save a deer struck by their '
              'vehicle.',
  'title': 'A Rickle in Time'},
 {'episode': '2',
  'id_tvdb': '275274',
  'media': 'television',
  'season': '2',
  'series': 'Rick and Morty',
  'synopsis': 'Rick teaches Morty to drive while leaving Jerry at a popular '
              "day care made just for him. Morty's conscience has him hunt "
              'down an assassin rather than spending the day at an alien '
              'arcade.',
  'title': 'Mortynight Run'},
 {'episode': '3',
  'id_tvdb': '275274',
  'media': 'television',
  'season': '2',
  'series': 'Rick and Morty',
  'synopsis': 'Rick gets emotionally invested when meeting an old friend, '
              'while Beth and Jerry have a falling out after making a '
              'discovery under the garage.',
  'title': 'Auto Erotic Assimilation'}]


Searching for a movie by title and year using IMDb
--------------------------------------------------

>>> from mapi.providers import IMDb
>>> client = IMDb(year_delta=1)
>>> hits = client.search(title='The Goonies', year=1985)
>>> pprint(hits)
[{'id_imdb': 'tt0089218',
  'media': 'movie',
  'synopsis': 'In order to save their home from foreclosure, a group of '
              "misfits set out to find a pirate's ancient valuable treasure.",
  'title': 'The Goonies',
  'year': '1985'}]


Handling a search gone awry
---------------------------

>>> from mapi.providers import TMDb
>>> client = TMDb()
>>> try:
>>>     hits = client.search(id_imdb='invalid_id')
>>> except MapiNotFoundException:
>>>     hits = 'None found :('
>>> print(hits)
None found :(


Usage
=====

Installing
----------

- **pip:** ``pip install mapi``
- **source:** ``pip install .``


Provider Configuration
----------------------

+-------------+--------------------------------------------------------+---------+-------+
| Parameter   | Description                                            | Default | Notes |
+=============+========================================================+=========+=======+
| api_key     | Developer API key                                      | None    | [1]_  |
+-------------+--------------------------------------------------------+---------+-------+
| max_hits    | Restricts the maximum number of responses for a search | 15      |       |
+-------------+--------------------------------------------------------+---------+-------+
| year_delta  | Filters results around this value inclusively          | 5       |       |
+-------------+--------------------------------------------------------+---------+-------+


Searching
---------

The following table describes the permissible fields which may be used for a
given search query. Extra fields are simply ignored.

+----------+---------------------+-----------+------------------------+-------------+
| Field    | API                 | Type      | Description            | Notes       |
+==========+=====================+===========+========================+=============+
| id_imdb  | IMDb, TMDb, TVDb    | str       | IMDb movie id key      | [2]_ [3]_   |
+----------+---------------------+-----------+------------------------+-------------+
| id_tmdb  | TMDb                | str / int | TMDb movie id key      | [3]_ [4]_   |
+----------+---------------------+-----------+------------------------+-------------+
| id_tvdb  | TVDb series id key  | str / int | TVDb season id key     | [3]_ [4]_   |
+----------+---------------------+-----------+------------------------+-------------+
| title    | IMDb, TMDb          | str       | Feature's title        |             |
+----------+---------------------+-----------+------------------------+-------------+
| year     | IMDb, TMDb          | str / int | Feature's release year |             |
+----------+---------------------+-----------+------------------------+-------------+
| series   | TVDb                | str       | Series' name           |             |
+----------+---------------------+-----------+------------------------+-------------+
| season   | TVDb                | str / int | Series' airing season  |             |
+----------+---------------------+-----------+------------------------+-------------+
| episode  | TVDb                | str / int | Series' airing episode | [4]_        |
+----------+---------------------+-----------+------------------------+-------------+


Results
-------

Each provider is guaranteed to return the following fields for a successful
search as strings. Notice that they are largely the fields as the search
parameters-- in fact, you can even next search calls within each other if you
so desire.

+----------+------------+--------------------------------------------+
| Field    | API        | Description                                |
+==========+============+============================================+
| id_imdb  | IMDb       | IMDb movie id key                          |
+----------+------------+--------------------------------------------+
| id_tmdb  | TMDb       | TMDb movie id key                          |
+----------+------------+--------------------------------------------+
| id_tvdb  | TVDb       | TVDb season id key                         |
+----------+------------+--------------------------------------------+
| title    | IMDb, TMDb | Feature's title                            |
+----------+------------+--------------------------------------------+
| year     | IMDb, TMDb | Feature's release year                     |
+----------+------------+--------------------------------------------+
| synopsis | ALL        | Media synopsis                             |
+----------+------------+--------------------------------------------+
| media    | ALL        | Media type; either 'movie' or 'television' |
+----------+------------+--------------------------------------------+
| series   | TVDb       | Series' name                               |
+----------+------------+--------------------------------------------+
| season   | TVDb       | Series' airing season                      |
+----------+------------+--------------------------------------------+
| episode  | TVDb       | Series' airing episode                     |
+----------+------------+--------------------------------------------+


Notes
=====
.. [1] required for TMDb and TVDb; alternatively, can be set by API_KEY_TMDB
       and API_KEY_TVDB enviroment variables, respectively
.. [2] id_imdb must be prefixed with 'tt'.
.. [3] Although ID, title, and series are each optional, movie queries must have
       either an ID or title to yield any results, and television queries must
       have either and ID or series to yield any results.
.. [4] If this field is passed as a string it must be numeric.

.. |licence| image:: https://img.shields.io/github/license/jkwill87/mapi.svg
   :target: https://en.wikipedia.org/wiki/MIT_License
.. |travis_ci| image:: https://img.shields.io/travis/jkwill87/mapi/develop.svg
   :target: https://travis-ci.org/jkwill87/mapi
.. |pypi| image:: https://img.shields.io/pypi/v/mapi.svg
   :target: https://pypi.python.org/pypi/mapi
.. |api| image:: https://img.shields.io/badge/api-IMDb/TMDb/TVDb-D8D200.svg
