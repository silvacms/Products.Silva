layout_macro = 'layout_macro.html'
#layout_folder = context.get_layout_folder()
#if layout_folder:
#    lm = getattr(layout_folder, layout_macro)
#else:
#    lm = getattr(context, layout_macro)
lm = getattr(context, layout_macro)
return lm.macros['layout']

