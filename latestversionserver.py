# Copyright (c) 2010, Christian L. Jacobsen
# All rights reserved. 
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
# 
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import os
import os.path
import sys
import json
import urllib
import wsgiref.util
from BaseHTTPServer import BaseHTTPRequestHandler

show_entries_re = re.compile('/([0-9]+)')

def render_404(environ, start_response):
    status = '404 %s' % BaseHTTPRequestHandler.responses[404][0]
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)

    return ['File not found: %s' % wsgiref.util.request_uri(environ, False)]

def render_500(environ, start_response, msg=None):
    if msg:
        if msg[:-1] != '\n': msg += '\n'
        msg = 'ERROR: ' + msg
        environ['wsgi.errors'].write(msg)
    status = '500 %s' % BaseHTTPRequestHandler.responses[500][0]
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)

    return [BaseHTTPRequestHandler.responses[500][0]]

import urlparse

def generate_download_json(config):
    data = dict(url = config['base_url'])
    for c in config['paths']:
        versions = get_versions(config, c)

        data[c[0]] = [
                dict(
                    version=c[3].match(x).group(1),
                    file=x,
                    path=urllib.pathname2url(os.path.join(c[0], x)),
                    url=urlparse.urljoin(config['base_url'], 
                        urllib.pathname2url(os.path.join(c[0], x)))) 
                for x in versions]

    return json.dumps(data)

def get_versions(config, path_config):
    fs_path = os.path.join(config['base'], path_config[1])
    fs_entries = os.listdir(fs_path)
    fs_entries = filter(lambda x: path_config[3].match(x), fs_entries)
    fs_entries.sort(path_config[2])

    return fs_entries

def latestversion_server(environ, start_response):
    path   = environ['PATH_INFO']
    config = environ['latestversion.config']

    if 'json_path' in config and path == config['json_path']:
        status = '200 OK'
        headers = [('Content-type', 'application/json')]
        start_response(status, headers)
        return [generate_download_json(config)]

    path_config = None
    for p in config['paths']:
        if path.startswith('/' + p[0]):
            path_config = p
            break
    if not path_config:
        return render_404(environ, start_response)

    versions = get_versions(config, path_config)

    match = show_entries_re.match(path[len(path_config[0]) + 1:])
    if match:
        result = '\n'.join(versions[-int(match.group(1)):])
    elif len(versions) == 0:
        result = ''
    elif len(path) == len(path_config[0]) + 2 and \
         path[len(path_config[0]) + 1] == '/':
        result = versions[-1]
    elif len(path) > len(path_config[0]) + 1:
        return render_404(environ, start_response)
    else:
        result = versions[-1]

    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [result]
 
if __name__ != '__main__':
    application = latestversion_server
else:
    from wsgiref.simple_server import make_server
    from wsgiref.validate import validator
    from wsgiref.simple_server import WSGIRequestHandler

    if len(sys.argv) == 2 and sys.argv[1] == 'reload':
        import paste.reloader as reloader
        reloader.install()
        print 'reloader installed'

    def test_server(environ, start_response):
        config = dict(
              base      = os.path.join(os.getcwd(), 'test'),
              base_url  = 'http://localhost:8000',
              json_path = '/downloads.json',
              paths = [
                  ('mac',
                   'mac',
                   cmp,   
                   re.compile('Application-mac-([0-9]{8}\.[0-9]{4})\.zip')),
                  ('win',
                   'win',
                   cmp,
                   re.compile('Application-win-([0-9]{8}\.[0-9]{4})\.zip'))])
        environ['latestversion.config'] = config
        return latestversion_server(environ, start_response)

    test_server = validator(test_server)

    httpd = make_server('', 8000, test_server)
    print "Serving on port 8000..."

    # Serve until process is killed
    httpd.serve_forever()
