import os, re
from dot_tools.text_tools import sep_bar
import pickle
from io import StringIO

TODO_DEFAULT_LABEL = 'Unlabeled'
TODO_DEFAULT_CATEGORY = None

class Todo:

    item_dict = None
    pickle_path = None
    label = None

    def __init__(self, path):
        self.pickle_path = os.path.expanduser(path)
        if os.path.exists(self.pickle_path):
            self.load()
        else:
            self.reset()

    def reset(self):
        self.item_dict = {
            'label' : TODO_DEFAULT_LABEL,
            'categories' : {
                TODO_DEFAULT_CATEGORY : [],
            },
        }

    def get_pickle_path(self):
        return os.path.abspath(self.pickle_path)

    def load(self):
        try:
            self.item_dict = pickle.load(open(self.pickle_path, 'rb'))
        except:
            raise IOError("Can't load todo list from extant storage file %s" % self.pickle_path)

    def save(self):
        try:
            pickle_file_handle = open(self.pickle_path, 'wb')
            pickle.dump(self.item_dict, pickle_file_handle)
        except Exception as er:
            raise IOError("Couldn't save todo list to storage file %s" % self.pickle_path)

    def set_label(self, label):
        try:
            label = str(label)
        except:
            raise ValueError("Couldn't use '%s' as a a lable" % label)
        if len(label) < 1:
            raise ValueError("Label must be at least 1 character long")
        self.item_dict['label'] = label

    def get_label(self):
        return self.item_dict['label']

    def add_item(self, item, category=TODO_DEFAULT_CATEGORY):
        if not self.has_category(category):
            self.item_dict['categories'][category] = [item,]
        elif item in self.item_dict['categories'][category]:
            message = "Todo list already contains '%s'" % item
            if category != TODO_DEFAULT_CATEGORY:
                message += " in category '%s'" % category
            raise ValueError(message)
        else:
            self.item_dict['categories'][category] += [item,]

    def __repr__(self):
        output = StringIO()
        header = self.item_dict['label']
        bar = sep_bar(bar_length=len(header))
        print(bar, file=output)
        print(header, file=output)
        print(bar, file=output)
        for category, items in list(self.item_dict['categories'].items()):
            indent = 0
            if category is not TODO_DEFAULT_CATEGORY:
                print(category + ':', file=output)
                indent = 2
            for item in items:
                print(' ' * indent + item, file=output)
        print(bar, file=output)
        return output.getvalue().rstrip()

    def delete_items(self, items_to_delete, category=TODO_DEFAULT_CATEGORY):
        if category not in self.item_dict['categories']:
            raise KeyError("No such category")
        for item in items_to_delete:
            self.item_dict['categories'][category].remove(item)
        if len(self.item_dict['categories'][category]) == 0:
            self.delete_category(category)

    def delete_category(self, category):
        if not self.has_category(category):
            raise KeyError("No such category")
        if category == TODO_DEFAULT_CATEGORY:
            self.item_dict['categories'][TODO_DEFAULT_CATEGORY] = []
        else:
            del self.item_dict['categories'][category]

    def has_category(self, category):
        return category in self.item_dict['categories']

    def get_items(self, category=TODO_DEFAULT_CATEGORY):
        if category not in self.item_dict['categories']:
            message = ''
            if category == TODO_DEFAULT_CATEGORY:
                message = "The todo list has no items at the base level"
            else:
                message = "The todo list has no such category '%s'" % category
            raise ValueError(message)
        else:
            return self.item_dict['categories'][category]

    def find_items(self, substring, category=TODO_DEFAULT_CATEGORY):
        if category not in self.item_dict['categories']:
            message = ''
            if category == TODO_DEFAULT_CATEGORY:
                message = "The todo list has no items at the base level"
            else:
                message = "The todo list has no such category '%s'" % category
            raise ValueError(message)
        else:
            matching_items=[]
            for item in self.item_dict['categories'][category]:
                if substring in item:
                    matching_items += [item,]
            return matching_items

