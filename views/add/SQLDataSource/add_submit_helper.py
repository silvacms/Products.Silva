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

model.manage_addProduct['Silva'].manage_addSQLDataSource(
    id, title)

SQLObject = getattr(model, id)

SQLObject.set_statement(sql_statement)
SQLObject.set_connection_id(connection_id)

if not parameters.find('\n'):
    parameters = parameters.replace('\r', '\n')
else:
    parameters = parameters.replace('\r', '')

parameters = parameters.split('\n')
for param in parameters:
    values = map(lambda s: s.strip(), param.split(':'))

    type = values[0]
    name = values[1]
    
    default_value = None
    description = ''
    if len(values) > 2:
        default_value = values[2]
        if len(values) > 3:
            description = values[3]
    SQLObject.set_parameter(
        name=name, type=type, default_value=default_value, 
        description=description)

#raise str(SQLObject.parameters())
return SQLObject
