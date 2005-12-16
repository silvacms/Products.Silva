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

# monkey patch to disable the spellchecker feature of Kupu if the spellchecker 
# binary can not be found: if the feature is used but the binary is not 
# available, the system goes into a spin(!)
def disable_spellchecker_if_necessary():
    from Products.kupu.python import spellcheck
    import os
    command = spellcheck.COMMAND
    if ' ' in command:
        command = command.split(' ')[0]
    pipe = os.popen('which %s 2> /dev/null' % command)
    try:
        path = pipe.read()
    finally:
        pipe.close()
    if not path.strip():
        print 'no %s found, monkey-patching Kupu' % command
        # we don't have the binary: disable
        class DummySpellChecker:
            def check(self, text):
                return {}
        spellcheck.SpellChecker = DummySpellChecker
        print 'dir spellcheck:', dir(spellcheck)
        print 'spellchecker:', spellcheck.SpellChecker
    else:
        print '%s found, not patching Kupu' % command
    
def patch_all():
    # perform all patches
    disable_spellchecker_if_necessary()
    fix_TALInterpreter_unicode_support()

