# Latestversionserver

>> Christian Jacobsen  
>>   <http://christian.lyderjacobsen.org/>  
>>   <http://www.absolutepanic.org/>

A Python/WSGI based webservice that reports the latest version of a
configurable set of files.

## License

The server is distributed under a BSD-style license.

## Files

* `latestversionserver.py`  
  The WSGI application.

* `latestversion.wsgi`  
  An example of how to configure and run the webservice for use with
    [mod\_wsgi][mod_wsgi]

## Use and Configuration

To use the latest version server you need a [wsgi][] compatible webserver. You
have a number of choices including [wsgiref.simple\_server][wsgisimple] and
[mod\_wsgi][mod_wsgi]. This documentation will show you how to set up the
latestversionserver using these two wsgi servers.

### wsgiref.simple_server

`wsgiref` is a standard python module as of Python 2.5. You can use this server
to test and experiment with the server. An example of how to configure the
server can be seen at the bottom of the `latestversionserver.py` file and more
help can be found in the [relevant Python documentation][wsgisimple]. An
example is also given below:

    import os
    import re
    from wsgiref.simple_server import make_server

    from latestversionserver import latestversion_server

    def test_server(environ, start_response):
        config = dict(
          base     = os.path.join(os.getcwd(), 'test'),
	  # url where version info should be served using the json format
	  # (optional)
	  json_path = '/downloads.json',
	  # base URL of the file server
	  # (only required if json_path is used)
	  base_url = 'http://localhost:8000',
          paths = [
              ('mac',    # url (relative)
               'mac',    # fs path (relative to base)
               cmp,      # compare function
               re.compile('Application-mac-[0-9]{8}\.[0-9]{4}\.zip'))])
        environ['latestversion.config'] = config
        return latestversion_server(environ, start_response)

    httpd = make_server('', 8000, test_server)
    httpd.serve_forever()

### mod_wsgi

Serving using [mod\_wsgi][mod_wsgi] is not too different from with
wsgiref.simple_server. An example can be found in `latestversion.wsgi`.

### Configuration

The configuration of the webservice happens by passing a dictionary to the
application using the environ variable. The dictionary should be set to the key
`latestversion.config` in the environ dictionary. See the two example files for
an example of how to do this. The dictionary contains two items. The key `base`
contains the base path in which files are found. This path is used in
conjunction with the information stored in the tuples contained in the
dictionary's `paths` key. Thus, `paths` should contain a list of tuples. Each
tuple contains four items, the first describing the (relative) URL at which
this tuple describes; the second describes the path (relative to base) where
the files reside; the third is a comparison function (sorting in ascending
order, see the Python documentation on [how to define a comparison function][com] or the [sorting tutorial][sortingtutorial]); and
finally the fourth item which is a regular expression defining the files in the
directory (specified as the second item) which have filenames that should be
considered for inclusion in finding the latest version.
 
      config = dict(
          base  = os.path.join(os.getcwd(), 'test'),
          paths = [
              ('mac',    # url (relative)
               'mac',    # fs path (relative to base)
               cmp,      # compare function
               re.compile('Application-mac-[0-9]{8}\.[0-9]{4}\.zip')),
              ('win',
               'win',
               cmp,
               re.compile('Application-win-[0-9]{8}\.[0-9]{4}\.zip'))])
               
               
### Using the webservice

The webservice exposes the URLs which you have defined in the configuration at
a location relative to where you have attached your webservice. For example, if
your webservice is running on `http://download.amazingapp.com/latest` then, if
you have configured your webservice as in the configuration example above, you
can see the latest Mac and Windows files at:

* `http://download.amazingapp.com/latest/mac` 
* `http://download.amazingapp.com/latest/win`

If you are running the `latestversionserver.py` file directly to test the
server, the following URLs are the ones you want to use:

* `http://localhost:8000/mac` 
* `http://localhost:8000/win`

Visiting these URLs returns a single line, the name of the latest file
according to the service. It is also possible to get more results than just the
most recent. This is done by appending a number to the URL, which indicates the
maximum number of results desired. For example, to display the five last
versions one would use the following URL:

* `http://download.amazingapp.com/latest/mac/5`

or if running the test server:

* `http://localhost:8000/mac/5`

Visiting this URL shows the 5 most recent files, one on each line, sorted in
ascending order. That is, the oldest one first, and the latest one last.

#### Special Cases

The webservice behaviour is as follows in these special cases:

* A filesystem path is referenced but it does not exist  
  
  __500 Server Error__

  This can, for example, happen when there is a configuration entry for a
  partciular path, but the path is not a directory or the directory does not
  exist.

* There are no files in a configured directory

  __200 OK__ but with no data, to indicate no latest version was found

* The user references a URL which has not been configured

  __404 File Not Found__

  URLs that have not been configured do not exist and return a 404.

[wsgi]:        http://wsgi.org/wsgi/
[mod_wsgi]:    http://code.google.com/p/modwsgi/
[wsgisimple]:  http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server
[cmp]: http://docs.python.org/library/functions.html#sorted
[sorttutorial]: http://wiki.python.org/moin/HowTo/Sorting/
