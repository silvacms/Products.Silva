import re, types

class DummyMessageID:
    """Dummy MessageID object

        is returned by the dummy MessageIDFactory, which is used
        when PlacelessTranslationService can not be imported.
    """
    mapping = None
    reg_interpolation = re.compile('\$\{([a-zA-Z0-9_]*)\}')
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, input):
        """store the input to return (untranslated) later on __str__()"""
        if not isinstance(input, basestring):
            input = str(input)
        self.__str = input
        self.__parsed = None
    
    def set_mapping(self, mapping):
        """Set a mapping for message interpolation
        """
        self.mapping = mapping

    def translate(self):
        """Return a stringified version of the input

            values in the form ${<varname>} are interpolated from
            self.mapping (if available)
        """
        if self.__parsed is not None:
            return self.__parsed
        if self.mapping is None and not self.reg_interpolation.search(self.__str):
            return self.__str
        s = self.__str
        mapping = self.mapping
        while 1:
            match = self.reg_interpolation.search(s)
            if not match:
                break
            try:
                rep = mapping[match.group(1)]
                if type(rep) not in types.StringTypes:
                    rep = str(rep)
                s = s.replace(match.group(0), rep)
            except KeyError:
                raise KeyError, match.group(1)
        self.__parsed = s
        return s

    def __str__(self):
        return self.translate()

def DummyMessageIDFactory(input, domain=None):
    return DummyMessageID(input)

