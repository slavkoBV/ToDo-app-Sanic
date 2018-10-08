#  Helper for Google Keep

import gkeepapi


class KeepAPIClient:
    def __init__(self, username, password):
        self.keep = gkeepapi.Keep()
        if username and password:
            self.keep.login(username, password)

    def sync(self):
        try:
            self.keep.sync()
        except Exception as err:
            print(err)

    def get_all_nodes(self):
        return self.keep.all()
