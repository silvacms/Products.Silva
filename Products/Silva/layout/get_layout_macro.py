## Script (Python) "get_layout_macro"
layout_macro = 'layout_macro.html'
lm = getattr(context, layout_macro)
return lm.macros['layout']

