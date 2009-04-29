Directory structure is a standard one for gettext:

* a directory per language code (en, de, fr, etc)

* in there, a LC_MESSAGES directory

* in there, a silva.po *and* a silva.mo file for that language. The
  silva.mo file can be generated using the `msgfmt` tool.

There's also a silva.pot file containing the default msgids.

Please consider helping us translate silva into your language, or
perfecting an existing translation. Translations can be edited online,
one string at a time. Silva's translations are found here:

https://launchpad.net/products/silva/+series/main/+pots/silva/
