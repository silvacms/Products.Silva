##parameters=id, status_code

from Products.Silva.helpers import IdCheckValues
view = context

if status_code == IdCheckValues.ID_CONTAINS_BAD_CHARS:
    return """Sorry, bad characters are in the id. It should only contain letters, digits and &quot;_&quot; or &quot;-&quot; or &quot;.&quot;.<br />
Spaces are not allowed in URLs, and the id should start with a letter or digit.<br />
You entered the id &#xab;%s&#xbb; which did not match these constraints.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_RESERVED_PREFIX:
    # FIXME: needs to know about the prefix
    prefix = id.split('_')[0]+'_'
    return """Sorry, ids starting with &#xab;%s&#xbb; are reserved for internal use.<br />
Please use another id.""" % view.quotify(prefix)

elif status_code == IdCheckValues.ID_RESERVED:
    return """Sorry, the id &#xab;%s&#xbb; is reserved for internal use.<br />
Please use another id.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_CONTENT:
    return """There is already an object with the id &#xab;%s&#xbb; in this container.<br />
Please use a different one.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_ASSET:
    return """There is already an asset with the id &#xab;%s&#xbb; in this container.<br />
Please use another id.""" % view.quotify(id)


# this should not happen
return """(Internal Error): An invalid status %s occured while checking the id &#xab;%s&#xbb;.<br />
Please contact the person responsible for this Silva installation or file a bug report yourself.""" % (view.quotify(status_code), view.quotify(id))

