# This will check that versions of dynamic c libraries used by lxml
# are not different than the one it was compiled against.
from lxml import etree
import logging

logger = logging.getLogger('silva.transform.renderer')

libxml  = etree.LIBXML_VERSION == etree.LIBXML_COMPILED_VERSION
libxslt = etree.LIBXSLT_VERSION == etree.LIBXSLT_COMPILED_VERSION

message = """%s used %s and compiled %s versions differ. It is likely that \
ld library path is incorrect (see: man ld.so)"""

if not libxml:
    logger.error(
        message %
            ('libxml', etree.LIBXML_VERSION, etree.LIBXML_COMPILED_VERSION,))

if not libxslt:
    logger.error(
        message %
            ('libxml', etree.LIBXSLT_VERSION, etree.LIBXSLT_COMPILED_VERSION,))
