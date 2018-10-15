#  Helper for Google Keep
# Username and password from Google Account
# To unblock access to Google Account from web-browser
# click Next on https://accounts.google.com/b/0/DisplayUnlockCaptcha

import gkeepapi


class KeepAPIClient:
    def __init__(self, username, password):
        self.keep = gkeepapi.Keep()
        if username and password:
            self.keep.login(username, password)

    async def get_list_by_title(self, title):
        lst = [i for i in self.keep.all() if i.title == title]
        return lst[0] if len(lst) > 0 else []

    async def sync_todo_list(self, tasks):
        """Synchronize Google Keep ToDo_list with tasks table from database

        :param tasks: list of tasks [(task.title, task.checked)]
        task.checked = True if task.status is 'Done', otherwise False
        :return: None
        """
        lst = await self.get_list_by_title('ToDo')  # Only one ToDo_list for one user
        if not isinstance(lst, gkeepapi.node.List):
            self.keep.createList('ToDo', tasks)
            self.keep.sync()
        else:
            items = [(item.text, item.checked) for item in lst.items]  # Items in Google Keep TodoList
            items_titles = [item.text for item in lst.items]
            tasks_titles = [task[0] for task in tasks]
            new_tasks = list(set(tasks) - set(items))
            deleted_tasks = list(set(items_titles) - set(tasks_titles))
            for task in new_tasks:
                if task[0] in items_titles:
                    for item in lst.items:
                        if (item.text == task[0]) and (item.checked != task[1]):
                            item.checked = task[1]
                else:
                    lst.add(*task)
            for item in lst.items:
                if item.text in deleted_tasks:
                    item.delete()
            self.keep.sync()
