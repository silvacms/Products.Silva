#
# This code is not here to stay. It is an experimental "proof of concept"
# implementation for resticting view access on Silva objects based on
# ip addresses. We need a more generic approach integrated in the silva core
# (e.g. based on roles?)
#
# This code is based on Clemens Klein-Robbenhaar's "CommentParser.py", 
# Marc Petitmermet's and Wolfgang Korosec's code.
#

import string
from Products.Silva.helpers import parseAccessRestriction

model = context
request = context.REQUEST
response = request.RESPONSE

show_document = 0
data_found = 1

restrict = parseAccessRestriction(model)

def inside(l, r):
    # Simplistic ip-range check
    l = l.split('.')
    r = r.split('.')[:len(l)]
    mapping = map(None, l, r)
    for local, remote in mapping:
	if local != remote:
           return 0
    return 1

if restrict.has_key('allowed_ip_addresses'):
    allowed_ip_addresses = restrict['allowed_ip_addresses']
    remote_addr = str(request.REMOTE_ADDR)
    
    if 'NONE' in allowed_ip_addresses:
        show_document = 0
    elif 'ALL' in allowed_ip_addresses:
        show_document = 1
    else:
        for addr in allowed_ip_addresses:
            if inside(addr, remote_addr):
                show_document = 1
                break
else:
    show_document = 1

if show_document:
    return context.index_html()
else:
    return "Access Restricted"
