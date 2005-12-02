def fix_TALInterpreter_unicode_support():
    """very cool patch

        In TALInterpreter at some point (do_i18nVariable, a piece of code that
        handles i18n:name directives) 'str()' is called on the value returned
        by tal:replace. If that value is a unicode string, the str() call fails
        with an exception (UnicodeError). To avoid this (so to allow combining
        unicode values with i18n:name) we replace the default (Python core)
        str() function with some other function 
        (DocumentTemplate.DT_Util.ustr()) that does know how to handle unicode 
        strings correctly.
    """
    from TAL import TALInterpreter
    TALInterpreter.str = TALInterpreter.ustr

def monkey_zope3_message_id():
    """Unfortunately we have to convince the Zope 3 message id of a few things.

    * set_mapping function exists

    * set_mapping (and friends..) can be used from Python scripts.
    """
    
    from zope.i18nmessageid.messageid import MessageID

    # monkey patch set_mapping into zope 3 message id..
    def set_mapping(self, d):
        self.mapping = d

    MessageID.set_mapping = set_mapping

    # and open it up for Zope 2...
    MessageID.__allow_access_to_unprotected_subobjects__ = True

def patch_all():
    # perform all patches
    fix_TALInterpreter_unicode_support()
    monkey_zope3_message_id()
