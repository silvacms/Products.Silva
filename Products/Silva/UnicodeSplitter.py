
import zope.deferredimport
import silva.core.services


zope.deferredimport.deprecated(
    'Please run zodbupdate.',
    Splitter=silva.core.services.splitter.Splitter)

