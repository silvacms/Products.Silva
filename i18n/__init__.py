try:
    from Products.PlacelessTranslationService.MessageID import MessageIDFactory
    translate = MessageIDFactory('silva')
except ImportError:
    translate = lambda x: x
