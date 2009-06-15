##parameters=objects,action,path=[],argv=[]
from Products.Silva.i18n import translate as _
from zope.i18n import translate

success = []
failed = []
no_date_refs = []

get_name = context.tab_status_get_name

for obj in objects:
    pathURL = "/".join(path)
    if len(pathURL) > 0:
        pathURL += "/"
    if not obj.implements_versioning():
        if not obj.implements_publication() and not obj.implements_container(): #The current object cannot be a folder or a publication
            failed.append((pathURL + get_name(obj), _('not applicable')))
        else:            
            returnStatus = []
            path.append(get_name(obj))
            if (obj.implements_container()): #Folder or other container
                returnStatus = context.do_publishing_action(obj.get_container().objectValues(), action, path, argv)
            else: #Publication
                returnStatus = context.do_publishing_action(obj.get_publication().objectValues(), action, path, argv)
            path.pop()

            success.extend(returnStatus[0])
            failed.extend(returnStatus[1])
            no_date_refs.extend(returnStatus[2])
        continue

    (flag,result) = action(obj,pathURL + get_name(obj),argv)
    if flag:
        success.append(result)
    else:
        if len(result) == 2:
            failed.append(result)
        else:
            failed.append((result[0], result[1]))
            no_date_refs.append(result[2])
    
return [success,failed,no_date_refs]
