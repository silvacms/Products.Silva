Running tests
=============

You need ZopeTestCase. It needs to be installed in your SOFTWARE_HOME
in lib/python/Testing. Currently there is no released version that
works, unfortunately; you need to check a version from CVS at the
Plone Collective (http://collective.sourceforge.net).

In an INSTANCE_HOME setup you need to set environment variables to the
right places:

  INSTANCE_HOME to /path/to/zope_instance

  SOFTWARE_HOME to /path/to/zope_software/lib/python

Setting environment variables in bash is like:
    
  export INSTANCE_HOME=/path/to/zope_instance

Don't worry that the test runner reports a different INSTANCE_HOME
when actually running; this is normal.

(People who don't run INSTANCE_HOME, please supply instructions how to
run tests in your setup here.)
 
Individual test modules have the 'test_' prefix. You can run these
individual modules with Python (the same Python version as the one
your Zope is running with):

  python test_foo.py

You can also run all test modules automatically:

  python runalltests.py

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

Status
======

This is a temporary list showing the status of the test suite. This
list will go away in the future as all test modules always have to
work.

test_CatalogedVersioning .. errors 1 (to do with catalog, test in 2.6.2)
test_Container           .. ok
test_Copy                .. broken
test_Ghost               .. errors 1 (render_view issue)
test_Publishable         .. ok
test_Security            .. ok
test_ServiceLayouts      .. broken (can't test without product installed..)
test_SilvaObject         .. ok
test_SimpleMembership    .. ok
test_VersionedContent    .. ok
test_Versioning          .. ok
test_catalog             .. ok
test_convert             .. ok
test_file                .. ok
test_icon                .. ok
test_mangle              .. ok

runalltests result: 

119 tests, failures=9, errors=11

  


