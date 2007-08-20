import os, tempfile

def execute(cmd):
    try:
        import win32pipe
        popen = win32pipe.popen4
    except ImportError:
        popen = os.popen4

    fp_in, fp_out = popen(cmd)
    fp_in.close()
    data = fp_out.read()
    fp_out.close()

    return data       

PDF_TO_TEXT_AVAILABLE = execute('pdftotext -v -').startswith('pdftotext')
WORD_TO_TEXT_AVAILABLE = execute('antiword -v').startswith('antiword') 

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

        #converted = execute('antiword -f -m UTF-8 "%s" -' % fname)
        converted = execute('antiword "%s"' % fname)

        os.unlink(fname)
        if converted.endswith('is not a Word Document.') or converted.startswith(
            "I'm afraid"):
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully.
            <span class="error">
                The uploaded file does not appear to be a valid Word file.
            </span>"""
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
        
        converted = execute('pdftotext -enc UTF-8 "%s" -' % fname)    

        os.unlink(fname)
        if 'PDF file is damaged' in converted:
            request.form['message_type']='feedback'
            request.form['message'] = """File uploaded succesfully. 
            <span class="error">
                The uploaded file does not appear to be a valid PDF file.
            </span>"""
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

