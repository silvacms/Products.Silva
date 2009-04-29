##parameters=format
# $Id: getDocmaFormatName.py,v 1.4 2004/11/16 18:18:52 eric Exp $
from Products.Silva.i18n import translate as _

formats = {
    'silva': _('Silva XML'),
    'word': _('Word document'),
}

return formats.get(format, _('unknown format'))


