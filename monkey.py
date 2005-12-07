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

from zope.i18nmessageid import MessageID
from TAL.TALInterpreter import ustr
def silva_do_insertStructure_tal(self, (expr, repldict, block)):
    structure = self.engine.evaluateStructure(expr)
    if structure is None:
        return
    if isinstance(structure, MessageID):
        # translate structure
        structure = self.engine.translate(structure.domain,
                                          structure,
                                          structure.mapping,
                                          default=structure.default)
    if structure is self.Default:
        self.interpret(block)
        return
    text = ustr(structure)
    if not (repldict or self.strictinsert):
        # Take a shortcut, no error checking
        self.stream_write(text)
        return
    if self.html:
        self.insertHTMLStructure(text, repldict)
    else:
        self.insertXMLStructure(text, repldict)
    
def fix_TALInterpreter_structure_i18n():
    """Silva relies on the TAL interpreter to translate

    tal:content="structure .." as well; the Zope 2 TAL interpreter
    doesn't do it.
    We monkey it with our own do_insertStructure_tal so to make it happen...
    """
    from TAL.TALInterpreter import TALInterpreter
    TALInterpreter.bytecode_handlers['insertStructure'] = silva_do_insertStructure_tal
    TALInterpreter.bytecode_handlers_tal['insertStructure'] = silva_do_insertStructure_tal
    
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

    # XXX opening up of MessageID further is done in Formulator, which
    # also needs it.. Since Silva depends on Formulator this is okay for now

def allow_translate():
    """Allow the importing and use of the zope.i18n.translate function
    in page templates.
    """
    from AccessControl import allow_module
    # XXX is this opening up too much..?
    allow_module('zope.i18n')
    
def patch_all():
    # perform all patches
    fix_TALInterpreter_unicode_support()
    fix_TALInterpreter_structure_i18n()
    monkey_zope3_message_id()
    allow_translate()
