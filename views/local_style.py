request = context.REQUEST
model = request.model

if model.implements_container():
    return '<!-- td.tab {background:#4d755b} -->'
else:
    return None
