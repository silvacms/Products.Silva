"""Call a URL, over HTTP or HTTPS, optionally using login credentials. This 
    can be used to update the publication status of all objects of which 
    either the publication_datetime or the expiration_datetime have passed, 
    since the system leaves them in the old state until they're called 
    (viewed).
"""

import urllib2, base64, urlparse

def call_url(proto, hostname, path, port=None, username=None, password=None):
    """Simply calls a URL, can be HTTP or HTTPS and login is supported"""
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener()
    opener.add_handler(handler)
    if port is not None:
        url = '%s://%s:%s%s' % (proto, hostname, port, path)
    else:
        url = '%s://%s%s' % (proto, hostname, path)
    request = urllib2.Request(url)
    if username and password:
        upw = base64.encodestring('%s:%s' % (username, password))[:-1]
        request.headers['Authorization'] = 'Basic %s' % upw
    response = opener.open(request)

if __name__ == '__main__':
    import sys
    if not len(sys.argv) == 2:
        print 'Usage: %s <URL>' % sys.argv[1]
        print
        print 'URL has the format \'proto://[user:pass@]hostname[:port]/path\''
        sys.exit()

    proto, loc, path, parms, query, frag = urlparse.urlparse(sys.argv[1])

    username = None
    password = None
    port = None
    if loc.find('@') > -1:
        up, loc = loc.split('@')
        username, password = up.split(':')
    if loc.find(':') > -1:
        loc, port = loc.split(':')
    
    call_url(proto, loc, path, port, username, password)
