request = context.REQUEST
model = request.model

if model.implements_container():
    return '<!-- td.tab {background:#4c7469} -->'
else:
    return None
