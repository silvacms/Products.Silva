from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import re

class Splitter:
    
    rx = re.compile(r"\w+", re.UNICODE)
    rxGlob = re.compile(r"\w+[\w*?]*", re.UNICODE)

    def process(self, lst):
        result = []
        for s in lst:
            result += self.rx.findall(s)
        return result

    def processGlob(self, lst):
        result = []
        for s in lst:
            result += self.rxGlob.findall(s)
        return result

splitter_name = 'Unicode Whitespace splitter'

if splitter_name not in element_factory.getFactoryNames('Word Splitter'):
    element_factory.registerFactory('Word Splitter',
                                    splitter_name,
                                    Splitter)

if __name__ == "__main__":
    import sys
    splitter = Splitter()
    for path in sys.argv[1:]:
        f = open(path, "rb")
        buf = f.read()
        f.close()
        print path
        print splitter.process([buf])
