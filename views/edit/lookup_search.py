##parameters=name=None
request = context.REQUEST
session = request.SESSION
model = request.model
view = context

if not name:
    name = request.form.get('name', ' ')
name = name.strip()

if name == '':
    return view.tab_access_lookup(
        message_type="error", 
        message="No search string supplied.")

if len(name) < 2:
    return view.tab_access_lookup(
        message_type="error", 
        message="Search string '%s' is too short. Please try a longer search string." % name)       

results = model.sec_find_users(name)
if not results:
    return view.tab_access_lookup(
        message_type="feedback", 
        message="No users found for search string '%s'." % name)

return view.tab_access_lookup(
    message_type="feedback", 
    message="Searched for '%s'." % name,
    results=results)

