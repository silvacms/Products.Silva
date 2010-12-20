##############################################################################
#
# Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################

# $Id: Makefile 16388 2005-08-24 14:10:09Z mihxil $

XSLTPROC = /usr/bin/env xsltproc
XSL_DEBUG = --param debug true\(\)
XSLTPROC_PARAMS = --nonet --novalid --xinclude
XSL_FILE = ../../kupu/make.xsl

all: clean silvamacros popup

silvamacros:
	$(XSLTPROC) $(XSLTPROC_PARAMS) -o kupumacros.html $(XSL_FILE) dist.kupu

clean:
	rm -f kupumacros.html kupupopup.html

popup:
	$(XSLTPROC) $(XSLTPROC_PARAMS) -o kupupopup.html $(XSL_FILE) dist-popup.kupu

