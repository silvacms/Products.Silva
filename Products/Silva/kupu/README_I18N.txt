Internationalization mechanism
==============================

To extract the i18n strings from the kupu directory, build the Kupu macros
using the commmands::

  $ cd <path_to_silva>/Silva/kupu
  $ make

Then use the latest i18nextract-sa product (0.9.2 or higher), and execute::

  $ i18nextract -d kupu -p <path_to_silva>/Silva/kupu -o <path_to_silva>/Silva/i18n

In all commands '<path_to_silva>' should be replaced with the full path to the
directory containing the Silva product (note that only the -o option requires
a full path).

After running these commands, the 'kupu.pot' file is build in Silva/i18n, which
can be copied to the language directories, and from those the .mo files can be
compiled or merged.

A couple of notes:

  * the macro uses plain Zope i18n statements, so this means that the i18n:
    attributes will need to be added to the .kupu files, which form the sources
    for the kupumacros.html file (do not modify kupumacros.html directly, as
    changes will be discarded next time 'make' is executed).

  * strings from the JavaScript files will need to be added to the 'i18n.kupu'
    XML 'island', this to avoid having to modify the i18nextract tool to find
    and parse JavaScript files, and traverse both the Kupu and Silva products
    for a single domain - iow: if you modify or add a string to the .js files,
    the i18n.kupu file will need to be updated
