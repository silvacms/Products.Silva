## Script (Python) "hex_from_str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=
##
bgcolor=''
for i in name:
  bgcolor = bgcolor + str(ord(i) - 96)
if len(name) < 6:
  for j in range(7-len(name)):
    bgcolor = bgcolor + 'F'
bgcolor = bgcolor[0:6]
bgcolor = '#' + bgcolor
return bgcolor
