Running tests
=============

You need ZopeTestCase, version 0.9.8 or higher.

It needs to be installed in your SOFTWARE_HOME in lib/python/Testing. You
can download released versions of ZopeTestCase here:

  http://www.zope.org/Members/shh/ZopeTestCase

To run the Silva tests you can use the ``test`` subcommand of ``zopectl``
of your Zope instance. So, assuming the current working directory is your
Zope instance::

  ./bin/zopectl test --dir Products/Silva

In case you'd like to run only one particular set of tests you can do this::

  ./bin/zopectl test --dir Products/Silva test_silvaviews

There're a lot more options for the test subcommand. For more information
you can issue::

  ./bin/zopectl test --help

Writing tests
=============

Your test module should have the prefix 'test_'. No other modules that
start with the prefix 'test' (even without underscore) should exist in
the tests directory, so don't create one. This is because
runalltests.py automatically looks for these modules.

Test methods should also start with the prefix 'test_'. Don't add
docstrings to test methods, as they'll make finding failing tests
slightly harder to find, as the docstring will show up in the test
output instead of the method name. Use comments (#) instead.

There is an example test module in skel.py. You can copy this for your
own modules.

Useful information:

  * Zope root: self.app

  * Silva root: self.root

  * Default username: 'test_user_1_'

  * Role of default user: 'ChiefEditor'

Troubleshooting
===============

If the test framework starts up but then before the first test is run
gives an error about persistence, you may have forgotten to import
SilvaTestCase.
