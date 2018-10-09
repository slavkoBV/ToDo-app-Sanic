#  Helper for Google Keep
# Username and password from Google Account
# To unblock access to Google Account from web-browser
# click Next on https://accounts.google.com/b/0/DisplayUnlockCaptcha

from typing import List
import gkeepapi


class KeepAPIClient:
    def __init__(self, username, password):
        self.keep = gkeepapi.Keep()
        if username and password:
            self.keep.login(username, password)

    def get_list_by_title(self, title):
        lst = [i for i in self.keep.all() if i.title == title]
        return lst[0] if len(lst) > 0 else []

    def sync_todo_list(self, tasks:List[(str, bool)]):
        """Synchronize Google Keep ToDo_list with tasks table from database

        :param tasks: list of tasks from database
        :return: None
        """
        lst = self.get_list_by_title('ToDo')
        if not isinstance(lst, gkeepapi.node.List):
            self.keep.createList('ToDo', tasks)
            self.keep.sync()
        else:
            res = list(set(tasks) - set([(item.text, item.checked) for item in lst.items]))
            for task in res:
                if task[0] in [item.text for item in lst.items]:
                    for item in lst.items:
                        if (item.text == task[0]) and (item.checked != task[1]):
                            item.checked = task[1]
                else:
                    lst.add(task)
            self.keep.sync()