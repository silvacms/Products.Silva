## Script (Python) "selectionSort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=list, item
##title=
##
#Inserts new items to the list so that it is sorted by title_or_id

bottom = 0
top = len(list)   
while bottom < top:
   mid = (bottom + top)/2
   if item.title_or_id() < list[mid].title_or_id(): 
      top = mid
   else: 
      bottom = mid+1
list.insert(bottom, item)
return ''
