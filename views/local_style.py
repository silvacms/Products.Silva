request = context.REQUEST
model = request.model

if model.implements_container():
    return '<!-- td.tab {background : #30805d;}-->'
else:
    return None