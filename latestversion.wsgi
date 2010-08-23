import re
from latestversionserver import latestversion_server

def configured_latestversion_server(environ, start_response):
    config = dict(
          base  = '/www/application-download/files',
          paths = [
              ('dev/mac',
               'mac-dev',
               cmp,
               re.compile('Application-mac-dev-[0-9]{8}\.[0-9]{4}\.zip')),
              ('dev/win/zip',
               'dev/win/zip',
               cmp,
               re.compile('Application-win-dev-[0-9]{8}\.[0-9]{4}\.zip'))
               ]
    )
    environ['latestversion.config'] = config
    return latestversion_server(environ, start_response)
    
application = configured_latestversion_server
