#  Helper for Google Keep
# Username and password from Google Account
# To unblock access to Google Account from web-browser
# click Next on https://accounts.google.com/b/0/DisplayUnlockCaptcha

import gkeepapi


class AuthException(gkeepapi.exception.LoginException):
    def __init__(self, message):
        super().__init__(message)


class KeepAPIClient:
    def __init__(self, username, password):
        self.keep = gkeepapi.Keep()
        try:
            self.keep.login(username, password)
        except gkeepapi.exception.LoginException:
            raise AuthException('User is unauthorised')

    async def get_list_by_title(self, title):
        lst = [i for i in self.keep.all() if i.title == title]
        return lst[0] if len(lst) > 0 else []

    async def get_new_tasks(self, tasks, items):
        """Return list of new tasks, that not in Google Keep items
        or tasks which status is changed.

        Args:
            tasks: list of tasks from database [(task.title, task.status)]
            items: dictionary of items from Google Keep {item.text, item.checked}
        """
        keep_items = set([(text, checked) for text, checked in items.items()])
        return list(set(tasks) - set(keep_items))

    async def sync_todo_list(self, tasks):
        """Synchronize Google Keep ToDo_list with tasks from database.

        Args:
            tasks: list of tasks [(task.title, task.status)]
            task.checked = True if task.status is 'Done', otherwise False
        """

        lst = await self.get_list_by_title('ToDo')  # Only one ToDo_list for one user
        if not isinstance(lst, gkeepapi.node.List):
            self.keep.createList('ToDo', tasks)
            self.keep.sync()
        else:
            items = {item.text: item.checked for item in lst.items}
            new_tasks = await self.get_new_tasks(tasks, items)
            deleted_tasks = list(set(items.keys()) - set([task[0] for task in tasks]))
            for task in new_tasks:
                if task[0] in items.keys():
                    for item in lst.items:
                        if (item.text == task[0]) and (item.checked != task[1]):
                            item.checked = task[1]
                else:
                    lst.add(*task)
            for item in lst.items:
                if item.text in deleted_tasks:
                    item.delete()
            self.keep.sync()
