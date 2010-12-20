request = context.REQUEST
model = request.model

if model.implements_container():
    return '<!-- td.tab {background:#4e7661} -->'
else:
    return None
