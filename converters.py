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

def get_converter_for_mimetype(mimetype):
    converter = {
        'text/plain': TextConverter,
        'application/pdf':PDFConverter
    }.get(mimetype)

    if converter is None:
        return
    return converter()

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
            request.form['message_type']='error'
            request.form['message'] = 'Warning: The uploaded file does not appear to be a valid PDF file.'
            return None
        return unicode(converted, 'utf8')

class TextConverter(object):
    def convert(self, data, request):
        return data

