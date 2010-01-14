
# BBB import
import zope.deferredimport

zope.deferredimport.deprecated(
    'Please import from silva.translations instead, '
    'this import location will be removed in Silva 2.3.',
    translate = 'silva.translations:translate')
