try:
    from Products.PlacelessTranslationService.MessageID import MessageIDFactory
    translate = MessageIDFactory('silva', True)
except ImportError:
    translate = lambda x: x
