# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import urlparse

#### Hack of the day: don't fuck up your all DB if an interface is broken.

from OFS.Uninstalled import BrokenClass
BrokenClass.__iro__ = tuple()

#### End of hack of the day


# add some scheme to urlparse

SCHEME_HTTP_LIKE_CAPABILITIES = [
    'uses_relative',
    'uses_netloc',
    'uses_params',
    'uses_query',
    'uses_fragment',
]

EXTRA_SCHEMES = [
    ('itms',   SCHEME_HTTP_LIKE_CAPABILITIES),
    ('webcal', SCHEME_HTTP_LIKE_CAPABILITIES),
    ('tel', SCHEME_HTTP_LIKE_CAPABILITIES),
]

def add_scheme(scheme, capabilities):
    for capability in capabilities:
        schemes = getattr(urlparse, capability)
        if not scheme in schemes:
            schemes.append(scheme)

def update_url_parse_schemes():
    for (scheme, caps) in EXTRA_SCHEMES:
        add_scheme(scheme, caps)

update_url_parse_schemes()

# register this extension
from silva.core import conf as silvaconf
silvaconf.extension_name('Silva')
silvaconf.extension_title('Silva Core')
silvaconf.extension_depends([])

try:
    from Products.MaildropHost import MaildropHost
    MAILDROPHOST_AVAILABLE = True
except ImportError:
    MAILDROPHOST_AVAILABLE = False

MAILHOST_ID = 'service_mailhost'


def initialize_icons():
    from Products.Silva.icon import registry

    mimeicons = [
        ('application/msword', 'file_doc.png'),
        ('application/pdf', 'file_pdf.png'),
        ('application/postscript', 'file_illustrator.png'),
        ('application/sdp', 'file_quicktime.png'),
        ('application/vnd.ms-excel', 'file_xls.png'),
        ('application/vnd.ms-powerpoint', 'file_ppt.png'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'file_ppt.png'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'file_xls.png'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'file_doc.png'),
        ('application/x-javascript', 'file_js.png'),
        ('application/x-rtsp', 'file_quicktime.png'),
        ('application/x-sdp', 'file_quicktime.png'),
        ('application/x-zip-compressed', 'file_zip.png'),
        ('audio/aiff', 'file_aiff.png'),
        ('audio/basic', 'file_aiff.png'),
        ('audio/mid', 'file_aiff.png'),
        ('audio/midi', 'file_aiff.png'),
        ('audio/mp3', 'file_aiff.png'),
        ('audio/mp4', 'file_aiff.png'),
        ('audio/mpeg', 'file_aiff.png'),
        ('audio/mpeg3', 'file_aiff.png'),
        ('audio/wav', 'file_aiff.png'),
        ('audio/x-aiff', 'file_aiff.png'),
        ('audio/x-gsm', 'file_aiff.png'),
        ('audio/x-m4a', 'file_aiff.png'),
        ('audio/x-m4p', 'file_aiff.png'),
        ('audio/x-midi', 'file_aiff.png'),
        ('audio/x-mp3', 'file_aiff.png'),
        ('audio/x-mpeg', 'file_aiff.png'),
        ('audio/x-mpeg3', 'file_aiff.png'),
        ('audio/x-wav', 'file_aiff.png'),
        ('text/css', 'file_css.png'),
        ('text/html', 'file_html.png'),
        ('text/plain', 'file_txt.png'),
        ('text/xml', 'file_xml.png'),
        ('video/avi', 'file_quicktime.png'),
        ('video/mp4', 'file_quicktime.png'),
        ('video/mpeg', 'file_quicktime.png'),
        ('video/msvideo', 'file_quicktime.png'),
        ('video/quicktime', 'file_quicktime.png'),
        ('video/x-dv', 'file_quicktime.png'),
        ('video/x-mpeg', 'file_quicktime.png'),
        ('video/x-msvideo', 'file_quicktime.png'),
        ]
    for mimetype, icon_name in mimeicons:
        registry.registerIcon(
            ('mime_type', mimetype),
            '++resource++silva.icons/%s' % icon_name)

    misc_icons = [
        ('ghostfolder', 'folder', 'silvaghost_folder.gif'),
        ('ghostfolder', 'publication', 'silvaghost_publication.gif'),
        ('ghostfolder', 'link_broken', 'silvaghost_broken.png'),
        ('ghost', 'link_ok', 'silvaghost.gif'),
        ('ghost', 'link_broken', 'silvaghost_broken.png'),
    ]
    for klass, kind, icon_name in misc_icons:
        registry.registerIcon(
            (klass, kind),
            '++resource++silva.icons/%s' % icon_name)

initialize_icons()
