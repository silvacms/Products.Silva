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
    
def patch_all():
    # perform all patches
    fix_TALInterpreter_unicode_support()

