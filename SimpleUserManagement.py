
class SimpleUserManagement:
    def __init__(self):
        pass

    def find_users(self, object, search_string):
        userids = object.get_valid_userids()
        result = []
        for userid in userids:
            if userid.find(search_string) != -1:
                result.append(self.get_user_info(self, userid))
        return result
    
    def get_user_info(self, object, userid):
        return {
            'uid': userid,
            'cn': userid,
            #'mail': None,
            #'userclass': None,
            #'ou': [] 
            }
    
user_management = SimpleUserManagement()
