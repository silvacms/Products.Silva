"""
Basic API for transforming Silva-XML to other formats.

currently only transformation to and from

    eopro2_11 (aka RealObjects EditOnPro) 
    eopro3_0 (aka RealObjects EditOnPro) 

is supported.

"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.6 $'


class Transformer:
    """ Transform xml trees using pythonic xist-like
        specifications.  
    """
    from ObjectParser import ObjectParser
    from base import Context

    def __init__(self, source, target):
        """ provide a transformer from source to target 
            (and possibly back).
        """
        self.source = source
        self.target = target

        # Alex Martelli and other cowards would frown on me :-)
        exec "import %s as s ; import %s as t" %(source, target)

        self.source_spec = s
        self.target_spec = t
        self.source_parser = self.ObjectParser(self.source_spec)
        self.target_parser = self.ObjectParser(self.target_spec)

    def to_target(self, sourceobj, context=None, compacting=1):
        context = context or self.Context()
        node = self.source_parser.parse(sourceobj)
        if compacting:
            node = node.compact()
        return node.convert(context=context)

    def to_source(self, targetobj, context=None, compacting=1):
        context = context or self.Context()
        node = self.target_parser.parse(targetobj)
        if compacting:
            node = node.compact()
        return node.convert(context=context)

class EditorTransformer(Transformer):
    def __init__(self, editor):
        Transformer.__init__(self, editor+'.silva', editor+'.html')
