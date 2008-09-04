Running tests
=============

To run the Silva tests you can use the ``test`` subcommand of ``zopectl``
of your Zope instance. So, assuming the current working directory is your
Zope instance::

  ./bin/zopectl test -s Products.Silva

In case you'd like to run only one particular set of tests you can do this::

  ./bin/zopectl test -m Products.Silva.test.test_silvaviews

There're a lot more options for the test subcommand. For more information
you can issue::

  ./bin/zopectl test --help
