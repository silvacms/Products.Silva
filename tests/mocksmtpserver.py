import smtpd # present in python 2.x but undocumented until 2.4

class MockSMTPServer(smtpd.SMTPServer):
    """SMTP Server that keeps track of each message received.
    """
    def __init__(self):
        smtpd.SMTPServer.__init__(self, ('localhost', 8025), ('localhost', 25))
        self._msgs_received = {}

    def process_message(peer, mailfrom, rcpttos, data):
        msg_list = self._msgs_received.get(mailfrom, [])
        msg_list.append(MockMessage(rcpttos, data))
        self._msgs_received[mailfrom] = msg_list
        print "Processed %s" % mailfrom

    def getMessagesDict(self):
        return self._msgs_received

class MockMessage:
    def __init__(self, recipients, data):
        self.recipients = recipients
        self.data = data
