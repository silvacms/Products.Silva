##bind context=context
response = context.REQUEST.RESPONSE
headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
            ('Last-Modified', 
                DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
            ('Cache-Control', 'no-cache, must-revalidate'),
            ('Cache-Control', 'post-check=0, pre-check=0'),
            ('Pragma', 'no-cache'),
            ]

placed = []
for key, value in headers:
    if key not in placed:
        response.setHeader(key, value)
        placed.append(key)
    else:
        response.addHeader(key, value)
