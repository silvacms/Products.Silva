## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##

sql_statement = result['sql_statement']
parameters = result['parameters']
connection_id = result['connection_id']

model.manage_addProduct['Silva'].manage_addSQLDataSource(id, title)

sqlobject = getattr(model, id)
sqlobject.set_statement(sql_statement)
sqlobject.set_connection_id(connection_id)

parameters_dict = sqlobject.parameter_string_to_dict(parameters)
for name, (type, default_value, description) in parameters_dict.items():
    sqlobject.set_parameter(
        name=name, type=type, default_value=default_value, 
        description=description)

return sqlobject
