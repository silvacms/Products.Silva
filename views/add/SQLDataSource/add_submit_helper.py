##parameters=model, id, title, result

# parameters and statement get encoded into ascii since the
# underlying Z SQL Method does not work with unicode.

sql_statement = result['sql_statement']
parameters = result['parameters']
connection_id = result['connection_id']
data_encoding = result['data_encoding']

model.manage_addProduct['Silva'].manage_addSQLDataSource(id, title)

sqlobject = getattr(model, id)
sqlobject.set_statement(sql_statement.encode('ascii'))
sqlobject.set_connection_id(connection_id)
sqlobject.set_data_encoding(data_encoding)

parameters_dict = sqlobject.parameter_string_to_dict(
    parameters.encode('ascii'))
for name, (type, default_value, description) in parameters_dict.items():
    sqlobject.set_parameter(
        name=name, type=type, default_value=default_value, 
        description=description)

return sqlobject
