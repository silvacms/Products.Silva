code = context.get_code_object()

if not code:
    return '<span class="warning">[Code element is broken]</span>'

return code()
