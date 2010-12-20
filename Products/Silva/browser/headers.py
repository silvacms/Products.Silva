# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# Five
from DateTime import DateTime
from Products.Five import BrowserView

class Headers(BrowserView):
    """docstring
    """
    def set_content_type_and_nocache(self):
        """docstring
        """
        content_tags = self.set_content_type()
        cache_tags = self.set_nocache()
        return content_tags + '\n' + cache_tags

    def set_content_type(self):
        """docstring
        """
        return self.set_headers([('Content-Type', 'text/html; charset=UTF-8')])

    def set_nocache(self):
        """docstring
        """
        headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
            ('Last-Modified',
                DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
            ('Cache-Control', 'no-cache, must-revalidate'),
            ('Cache-Control', 'post-check=0, pre-check=0'),
            ('Pragma', 'no-cache'),
            ]
        return self.set_headers(headers)

    def set_headers(self, headers):
        """docstring
        """
        response = self.request.RESPONSE
        placed = []
        tags = []
        for key, value in headers:
            tags.append("""<meta http-equiv="%s" content="%s" />""" % (key, value))
            if key not in placed:
                response.setHeader(key, value)
                placed.append(key)
            else:
                response.addHeader(key, value)
        return '\n'.join(tags)
