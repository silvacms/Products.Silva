This subpackage only contains adapters. It is expected more and more
core code will be migrated to be adapter code as time progresses.

The coding style in this package is different than in core Silva:
  
   * camelCaseMethodNames

   * lowercase module names

   * try to import modules rather than classes or functions themselves,
     and then use namespace prefix. So instead of:

       from Products.Silva.adapters.adapter import Adapter

       foo = Adapter()

     use:

       from Products.Silva.adapters import adapter

       foo = adapter.Adapter()

In addition, we put much emphasis on getting the interfaces right in
the first place; instead of adding three messy methods to get the UI
working, focus on getting the abstraction right and have one method
instead. Sometimes the right abstraction is of course more methods,
not less.

