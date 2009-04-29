## Script (Python) "getBatch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=results, size=20, orphan=2, overlap=0
##title=Get current batch from results sequence
##

# got this script here:
# http://www.zopelabs.com/cookbook/1015785843
# Thanks to Casey Duncan

from ZTUtils import Batch

REQ = context.REQUEST

try:
    start_val = REQ.get('batch_start', '0')
    start = int(start_val)
    size = int(REQ.get('batch_size',size))
except ValueError:
    start = 0

batch = Batch(results, size, start, 0, orphan, overlap)

def getBatchLink(qs, new_start):
    if new_start is not None:
        if not qs:
            qs = 'batch_start=%d' % new_start
        elif qs.startswith('batch_start='):
            qs = qs.replace('batch_start=%s' % start_val,
                            'batch_start=%d' % new_start)
        elif qs.find('&batch_start=') != -1:
            qs = qs.replace('&batch_start=%s' % start_val,
                            '&batch_start=%d' % new_start)
        else:
            qs = '%s&batch_start=%d' % (qs, new_start)

        return qs

# create a new query string with the correct batch_start/end 
# for the next/previous batch
if batch.end < len(results):
    qs = getBatchLink(REQ.QUERY_STRING, batch.end)
    REQ.set('next_batch_url', '%s?%s' % (REQ.URL, qs))

if start > 0:
    new_start = start - size
    if new_start < 0: new_start = 0
    qs = getBatchLink(REQ.QUERY_STRING, new_start)
    REQ.set('previous_batch_url', '%s?%s' % (REQ.URL, qs))

return batch
