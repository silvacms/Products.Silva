##bind context=context
##parameters=size
"""convert size to a human readable format
    
    size: int, size of a file in bytes
    returns str, like '8.2M'
"""

magnitude = ['', 'K', 'M', 'G', 'T']

magnitude.reverse()
size = float(size)
threshold = 500
mag = magnitude.pop()

while size > threshold and magnitude:
    size = size / 1024
    mag = magnitude.pop()

if int(size) == size:
    return '%i%s' % (size, mag)
return '%.2f%s' % (size, mag)

