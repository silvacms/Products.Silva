##parameters=format
# $Id: getDocmaFormatName.py,v 1.3 2003/05/12 09:11:21 kitblake Exp $

formats = {
    'silva': 'Silva XML',
    'word': 'Word document',
}

return formats.get(format, 'unknown format')


