model = context.REQUEST.model

result = []
for userid in model.sec_get_userids_deep():
    email = model.sec_get_member(userid).email()
    if email is None or email.strip() == "":
        continue
    result.append(email)
return ", ".join(result)
