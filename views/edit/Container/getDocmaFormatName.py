##parameters=format
# $Id: getDocmaFormatName.py,v 1.2 2003/03/24 15:18:24 zagy Exp $

formats = {
    'silva': 'Silva XML',
    'word': 'Word Document',
}

return formats.get(format, 'unknown')


