# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# Five
from DateTime import DateTime
from Products.Five import BrowserView

class Headers(BrowserView):
    def __call__(self):
        self._setHeaders([('Content-Type', 'text/html; charset=UTF-8')])
        headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
            ('Last-Modified', 
                DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
            ('Cache-Control', 'no-cache, must-revalidate'),
            ('Cache-Control', 'post-check=0, pre-check=0'),
            ('Pragma', 'no-cache'),
            ]
        self._setHeaders(headers)
        
    def _setHeaders(self, headers):
        response = self.request.RESPONSE
        placed = []
        for key, value in headers:
            if key not in placed:
                response.setHeader(key, value)
                placed.append(key)
            else:
                response.addHeader(key, value)
