
class SimpleUserManagement:
    def __init__(self):
        pass

    def find_users(self, object, search_string):
        userids = object.acl_users.getUserNames()
        result = []
        for userid in userids:
            if userid.find(search_string) != -1:
                result.append(userid)
        return result
    
    def get_user_info(self, object, userid):
        return {
            'userid': userid,
            'name': name
            }
    
user_management = SimpleUserManagement()
