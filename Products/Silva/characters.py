# -*- coding: iso-8859-1 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt
import string

# this is file is separated out from mangle, as it is too easy to screw up
# the encoding with an editor otherwise

# the system currently relies on this to be in latin1 encoding, as in UTF-8
# encoding both strings arenot of equal length
bad_chars  = r""" ,:;()[]{}~`'"!@#$%^&*+=|\/<>?ÄÅÁÀÂÃäåáàâãÇçÉÈÊËÆéèêëæÍÌÎÏíìîïÑñÖÓÒÔÕØöóòôõøŠšßÜÚÙÛüúùûÝŸýÿŽž"""
good_chars = r"""______________________________AAAAAAaaaaaaCcEEEEEeeeeeIIIIiiiiNnOOOOOOooooooSssUUUUuuuuYYyyZz"""
char_transmap = string.maketrans(bad_chars, good_chars)
