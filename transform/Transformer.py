"""
Basic API for transforming Silva-XML to other formats.

currently only transformation to and from

    eopro2_11 (aka RealObjects EditOnPro) 

is supported.

"""

__author__='Holger P. Krekel <hpk@trillke.net>'
__version__='$Revision: 1.3.2.2 $'


class Transformer:
    """ Transform xml trees using pythonic xist-like
        specifications.  
    """
    from ObjectParser import ObjectParser

    def __init__(self, source='eopro2_11.silva', target='eopro2_11.html'):
        """ provide a transformer from source to target 
            (and possibly back).
        """
        self.source = source
        self.target = target

        # Alex Martelli and other cowards would frown on me :-)
        # XXX Guido: Not because I'm a coward or so, but can't this be done
        # using __import__?
        exec "import %s as s ; import %s as t" %(source, target)
        self.source_spec = s
        self.target_spec = t
        self.source_parser = self.ObjectParser(self.source_spec)
        self.target_parser = self.ObjectParser(self.target_spec)

    def to_target(self, sourceobj, context=None, compacting=1):
        context = context or {}
        node = self.source_parser.parse(sourceobj)
        if compacting:
            node = node.compact()
        return node.convert(context=context)

    def to_source(self, targetobj, context=None, compacting=1):
        context = context or {}
        node = self.target_parser.parse(targetobj)
        if compacting:
            node = node.compact()
        return node.convert(context=context)

class EditorTransformer(Transformer):
    def __init__(self, editor='eopro2_11'):
        if editor=='eopro2_11':
            Transformer.__init__(self, 
                                 source='eopro2_11.silva', 
                                 target='eopro2_11.html')
        elif editor == 'epoz':
            Transformer.__init__(self, 
                                 source='epoz.silva', 
                                 target='epoz.html')
        else:
            raise "Unknown Editor: %s" % editor
