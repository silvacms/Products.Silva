# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
import string

class EventHandler:
    """Handles events coming from parser. Two kinds of events exist;
    token events and text events. EventHandler constructs a list
    mapping structures to the text (or None if no structure can be mapped).
    """
    def __init__(self, structures):
        """Initialize the EventHandler; takes a list of structures
        that the event handler will try to associate with incoming text.
        """
        self.structures = structures

        self.start_tokens = {}
        for structure in self.structures:
            self.start_tokens[structure.start] = structure
        self.clear()

    def clear(self):
        """Clear the EventHandler so it can be restarted for new text.
        """
        self.current_structure = None
        self.current_structure_token = 0
        self.current_text_fragments = []

        self.result = []
        
    def get_result(self):
        """Get the result of the event handling; a list of tuples;
        either None and a string of text if no structure can be
        associated, or a structure and a list of text fragments inside
        that structure.
        """
        return self.result
    
    def structure_start(self, structure):
        """The start of a structure was encountered; prepare EventHandler
        to deal with that structure now.
        """
        self.current_structure = structure
        self.current_structure_token = 1
        self.current_text_fragments = []

    def structure_end(self):
        """The end of a structure was encountered; store the structure
        info in the result and notify the event handler not to record
        for structures anymore.
        """
        # store found text fragments in result associated with structure
        self.result.append((self.current_structure,
                            self.current_text_fragments))
        # we're not working on a structure anymore
        self.current_structure = None
        self.current_text_fragments = []
        
    def structure_abort(self):
        """A token was encountered that should not be in this structure.
        Abort the recording of text fragments and add those already recorded
        to the result (as text not associated with a structure).
        """
        # append the current text fragments as normal text instead
        self.result.append((None,
                            string.join(self.current_text_fragments, '')))
        # we're not working on a structure anymore
        self.current_structure = None
        self.current_text_fragments = []
        
    def get_expected_token(self):
        """Get the token that is expected by the current structure.
        """
        return self.current_structure.tokens[self.current_structure_token]

    def check_structure_end(self):
        """Returns true if an entire structure was encountered.
        """
        return self.current_structure_token == len(
            self.current_structure.tokens)
    
    def token_event(self, token):
        """A token is detected during parsing; handle it.
        """
        if not self.current_structure:
            # check if we start a new structure with this token
            structure = self.start_tokens.get(token, None)
            # if the token makes no sense, skip it
            if not structure:
                return    
            # start the structure if this token starts one
            self.structure_start(structure)
            return
        
        if token != self.get_expected_token():
            # if this isn't the expected token, abort structure
            self.structure_abort()
            # try again; perhaps a new structure is started
            self.token_event(token)
            return

        # we did get an expected token; increase counter by 1
        self.current_structure_token = self.current_structure_token + 1

        # check if the end of the structure was reached
        if self.check_structure_end():
            # finalize structure
            self.structure_end()
    
    def text_event(self, text):
        """Text is detected during parsing; handle it.
        """
        if not self.current_structure:
            # if we're not in a structure, just record text into result
            self.result.append((None, text))
        else:
            # we are in a structure, record text into current_text_fragments
            self.current_text_fragments.append(text)
        
class Structure:
    """A structure is list of tokens that can be encountered in the text.
    """
    def __init__(self, tokens):
        assert len(tokens) > 1
        self.tokens = tokens
        self.start = tokens[0]
        self.end = tokens[-1]
    
class Parser:
    """The parser goes throught the text and sends token events and
    text events to the associated event handler.
    """
    def __init__(self, handler, tokens):
        """Initialize the parser.
        """
        self.handler = handler
        # order tokens so largest lengths come in front; this'll cause
        # the larger token to be matched instead of a smaller one that
        # is contained in it
        tokens.sort(lambda x, y: len(y) - len(x))
        self.tokens = tokens
    
    def parse(self, s):
        """Parse the incoming string for tokens and text.
        """
        max = len(s)
        handler = self.handler
        start = 0
        while 1:
            # search for next token
            found_i = max
            found_token = None
            for token in self.tokens:
                i = string.find(s, token, start)
                if i != -1 and i < found_i:
                    found_i = i
                    found_token = token
            # first send a text event until token location (or end)
            handler.text_event(s[start:found_i])
            # if no token was found, we're done now
            if not found_token:
                # add any last unfinished text of a structure to the
                # list
                handler.structure_abort()
                return
            # we found a token, so handle it
            handler.token_event(found_token)
            # now skip over token
            start = found_i + len(found_token)

        
class ForgivingParser:
    """Combines the parser and event handler; associate structurse
    with text fragments. Tolerate incomplete structures.
    """
    def __init__(self, structures):
        """Initialize with a list of structures.
        """
        # create event handler
        self.eventhandler = EventHandler(structures)
        # create list of tokens
        token_dict = {}
        for structure in structures:
            for token in structure.tokens:
                token_dict[token] = None
        tokens = token_dict.keys()
        # create parser
        self.parser = Parser(self.eventhandler, tokens)

    def parse(self, s):
        """Parse the string and return the result.
        """
        self.eventhandler.clear()
        self.parser.parse(s)
        return self.eventhandler.get_result()




