## Script (Python) "connection_ids"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.Silva.SQLDataSource import available_connection_ids
return available_connection_ids(context)