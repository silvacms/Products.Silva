# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.ZCTextIndex.PipelineFactory import element_factory

import re

class Splitter(object):

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
try:
    element_factory.registerFactory('Word Splitter',
        'Unicode Whitespace splitter', Splitter)
except ValueError:
    # in case the splitter is already registred, ValueError is raised
    pass

if __name__ == "__main__":
    import sys
    splitter = Splitter()
    for path in sys.argv[1:]:
        f = open(path, "rb")
        buf = f.read()
        f.close()
        print path
        print splitter.process([buf])
