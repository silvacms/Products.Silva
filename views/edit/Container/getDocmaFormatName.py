##parameters=format
# $Id: getDocmaFormatName.py,v 1.1.4.1 2003/03/24 15:17:30 zagy Exp $

formats = {
    'silva': 'Silva XML',
    'word': 'Word Document',
}

return formats.get(format, 'unknown')


