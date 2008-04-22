import os, tempfile
from subprocess import Popen, PIPE


def execute(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    fp_err = p.stderr
    fp_out = p.stdout
    data = fp_out.read()
    fp_out.close()
    err = fp_err.read()
    fp_err.close()
    return err, data

PDF_TO_TEXT_AVAILABLE = execute('pdftotext -v -')[0].startswith('pdftotext')
WORD_TO_TEXT_AVAILABLE = execute('antiword -v')[0].startswith('antiword') 


def get_converter_for_mimetype(mimetype):
    converter = {
        'text/plain': TextConverter,
        'application/pdf':PDFConverter,
        'application/msword':WordConverter 
    }.get(mimetype)

    if converter is None:
        return
    return converter()


class WordConverter(object):

    def convert(self, data, request):
        if not WORD_TO_TEXT_AVAILABLE:
            return
        fname = tempfile.mktemp('.doc', 'silva_')
        fp = open(fname, 'w+b')
        fp.write(data)
        fp.close()
        err, converted = execute('antiword "%s"' % fname)
        os.unlink(fname)
        if err:
            # XXX This, as far as I can tell is never actually
            # presented back to the user. Did something change or did
            # this just never work?
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully.
            <span class="error">
            The uploaded file does not appear to be a valid Word file:
            <br /><br />%s
            </span>""" % err
            return None
        try:
            decoded = unicode(converted, 'utf8')
            return decoded
        except UnicodeDecodeError:
            return None


class PDFConverter(object):

    def convert(self, data, request):
        if not PDF_TO_TEXT_AVAILABLE:
            return
        fname = tempfile.mktemp('.pdf', 'silva_')
        fp = open(fname, 'w+b')
        fp.write(data)
        fp.close()
        err, converted = execute('pdftotext -enc UTF-8 "%s" -' % fname)
        os.unlink(fname)
        if err:
            # XXX This, as far as I can tell is never actually
            # presented back to the user. Did something change or did
            # this just never work?
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully. 
            <span class="error">
            The uploaded file does not appear to be a valid PDF file:
            <br /><br />%s
            </span>""" % err
            return None
        try:
            decoded = unicode(converted, 'utf8')
            return decoded
        except UnicodeDecodeError:
            return None


class TextConverter(object):
    def convert(self, data, request):
        try:
            decoded = unicode(data, 'utf8')
            return decoded
        except UnicodeDecodeError:
            return None

