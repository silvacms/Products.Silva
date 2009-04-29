##parameters=name=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
session = request.SESSION
model = request.model

if not name:
    name = request.form.get('name', ' ')

try:
    name = unicode(name, 'utf-8')
except TypeError:
    #already unicode. name could be coming from code *or* a
    #form. Obviously that sucks.
    pass

name = name.strip()

if name == '':
    return context.lookup_ui(
        message_type="error",
        message=_("No search string supplied."))

if len(name) < 2:
    msg = _("Search string '${string}' is too short. "
            "Please try a longer search string.", mapping={'string': name})
    return context.lookup_ui(
        message_type="error",
        message= msg)

results = model.sec_find_users(name)
if not results:
    msg = _("No users found for search string '${string}'.",
            mapping={'string': name})
    return context.lookup_ui(
        message_type="feedback",
        message= msg)

msg = _("Searched for '${string}'.", mapping={'string': name})
return context.lookup_ui(
    message_type="feedback",
    message=msg,
    results=results)

