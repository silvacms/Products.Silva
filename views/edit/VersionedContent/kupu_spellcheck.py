from Products.kupu.python.spellcheck import SpellChecker, format_result

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml;charset=UTF-8')

s = SpellChecker()
result = s.check(context.REQUEST['text'])
if result is None:
    result = ''
else:
    result = format_result(result)

return result
