import os, tempfile, subprocess


def execute(cmd):
    return subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


PDF_TO_TEXT_AVAILABLE = execute('pdftotext -v -')[1].startswith('pdftotext')
WORD_TO_TEXT_AVAILABLE = execute('antiword -v')[1].startswith('antiword') 


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
        converted, err = execute('antiword "%s"' % fname)
        os.unlink(fname)
        if err:
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully.
            <br /><span class="error">
            The uploaded file does not appear to be a valid Word file:
            <br /><br />%s
            </span>""" % "<br />".join(err.split("\n"))
        try:
            if converted:
                decoded = unicode(converted, 'utf8')
                return decoded
            return None
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
        converted, err = execute('pdftotext -enc UTF-8 "%s" -' % fname)
        os.unlink(fname)
        if err:
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully. 
            <br /><span class="error">
            The uploaded file does not appear to be a valid PDF file:
            <br /><br />%s
            </span>""" % "<br />".join(err.split("\n"))
        try:
            if converted:
                decoded = unicode(converted, 'utf8')
                return decoded
            return None
        except UnicodeDecodeError:
            return None


class TextConverter(object):
    def convert(self, data, request):
        try:
            decoded = unicode(data, 'utf8')
            return decoded
        except UnicodeDecodeError:
            return None

