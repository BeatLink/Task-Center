#!/usr/bin/env python3
"""

# string_rules
    # title
    # description

    # contains string
    # equal to string
    # exists

# date rules
    # start date
    # due date
    # done date
    # stop_date
    # Manual date


    # exists
    # is same as
    # is later than
    # is earlier than



# Recurrence enabled
# recurrence interval
# recurrence increment
# recurrence weekdays
# recurrence stop_type
# recurrence stop number
# recurrence weekday_of_month

# and
# or
# not

* Status tags (normal but preloaded)
    * Active
    * Current - has start date in past or no start date
    * Done - has done date set
"""





# default tags
# default tag behavior- description or title has tag

class Rule:

    def __init__(self):
        pass

        possible_attributes = [
            'start-date',
            'due-date',
            'repeat-enabled',
            'title',
            'description'
        ]

            # all repeated attributes]
    # rules have 3 logic, attribute, result and comparison



class Tag:

    def __init__(self):

        self.name = ''
        self.colour = None
        self.priority = 0 # changes the sort ordering of the tag in a lists
        self.ruleset = None  #  rulesets determine which tasks show ip under which tags.

        # ruleset 1: description or title has tag

        pass
    @property
    def data(self):
        return None

    @data.setter
    def data(self, data):
        pass


# Built in Tags --------------------------------------------------------------------------------------------------------
all_tasks = Tag()
all_tasks.name = 'All Tasks'
all_tasks.ruleset = True


# built in tags
# untagged
#!/usr/bin/env python3

import logging
import uuid
from collections import deque
import peewee

logger = logging.getLogger()

UNSET = "UNSET"

# Todo: Add comments and documentation here


# Relationship manager #################################################################################################
class RelationshipManager:
    """
    This class manages a hierarchial tree of objects.

    Methods
    * set_parent_node
    * get_children_nodes
    * get_parent_node
    * get_ancestor_nodes
    * get_sorted_noddes
    * delete_node

    """

    def __init__(self):
        self._parent_dict = {}
        self._ancestry_dict = {}  # derived from parent dict
        self._children_dict = {}  # derived from parent dict
        self._descendants_dict = {}  # derived from children dict

    def _determine_ancestry(self, node_id):
        ancestry_list = []
        parent = self._parent_dict[node_id]
        while parent:
            ancestry_list.append(parent)
            parent = self._parent_dict[parent]
        return ancestry_list

    def _determine_children(self, node_id):
        return {child for child, parent in self._parent_dict.items() if parent == node_id}

    def _determine_descendants(self, node_id):
        children = self._children_dict[node_id]
        for child in children.copy():
            children.update(self._determine_descendants(child))
        return children

    def _update_relationship(self, node_id):
        self._children_dict[node_id] = self._determine_children(node_id)
        self._ancestry_dict[node_id] = self._determine_ancestry(node_id)
        self._descendants_dict[node_id] = self._determine_descendants(node_id)

    def _update_all_relationships(self):
        for node_id in self._parent_dict:
            self._children_dict[node_id] = self._determine_children(node_id)
        for node_id in self._parent_dict:
            self._ancestry_dict[node_id] = self._determine_ancestry(node_id)
        for node_id in self._parent_dict:
            self._descendants_dict[node_id] = self._determine_descendants(node_id)

    # Public Methods ---------------------------------------------------------------------------------------------------
    def set_parent_node(self, node_id, parent_node_id):
        """This method sets parent_node_id as the parent of node id, then updates all the relationships"""
        self._parent_dict[node_id] = parent_node_id
        self._update_all_relationships()

    def delete_node(self, node_id):
        if node_id:
            del self._parent_dict[node_id]
            del self._children_dict[node_id]
            del self._ancestry_dict[node_id]
            del self._descendants_dict[node_id]
            self._update_all_relationships()

    def get_children_nodes(self, node_id):
        """Returns a lists of all the nodes descendants (all subnodes, the subnodes' subnodes and so on)"""
        return self._descendants_dict[node_id]

    def get_parent_node(self, node_id):
        return self._parent_dict[node_id]

    def get_ancestor_nodes(self, node_id):
        """Returns a sequential lists of the ancestry of a node (its parent, the parent's parent and so on"""
        return self._ancestry_dict[node_id]

    def get_sorted_nodes(self, node_list):
        """Sorts the node ids so that parent nodes come before child nodes. """
        node_list = deque(node_list)
        while len(node_list) > 0:
            node_id = node_list.pop()
            parent = self._parent_dict.get(node_id)
            if not parent or parent not in node_list:
                yield node_id
            else:
                node_list.appendleft(node_id)

    def load_from_dict(self, dict_object):
        self._parent_dict = dict_object['parents']
        self._children_dict = dict_object['children']
        self._ancestry_dict = dict_object['ancestry']
        self._descendants_dict = dict_object['descendants']

    def save_to_dict(self):
        return {
            'parents': self._parent_dict,
            'children': self._children_dict,
            'ancestry': self._ancestry_dict,
            'descendants': self._descendants_dict
        }


# Tree Manager #########################################################################################################
class TreeManager:
    def __init__(self, node_class, node_objects_dict=None, relationship_manager=RelationshipManager()):
        self._node_class = node_class
        self._dict = node_objects_dict if node_objects_dict else {}
        self._relationship_manager = relationship_manager

    def _create_node(self, node_object=None, parent=None):
        node_id = str(uuid.uuid4())
        self._update_node(node_id, node_object, parent=parent)
        return node_id

    def _read_node(self, node_id):
        if node_id in self._dict:
            return self._dict[node_id]

    def _update_node(self, node_id, node_object, parent=UNSET):
        self._dict[node_id] = node_object
        if parent != UNSET:
            self._relationship_manager.set_parent_node(node_id, parent)
        return node_id

    def _delete_node(self, node_id, delete_subnodes=False):
        if delete_subnodes:
            for child in self._relationship_manager.get_children_nodes(node_id):
                self._delete_node(child)
        if node_id in self._dict:
            self._relationship_manager.delete_node(node_id)
            del self._dict[node_id]

    @property
    def _all_node_ids(self):
        return self._dict.keys()


class TagManagerCore(TreeManager):
    def __init__(self, node_class=Tag):
        super().__init__(node_class)

    def get_all_tag_data(self):
        return ''

    def load_all_tag_data(self, tag_data):
        pass

    @property
    def tags(self):
        return [word.lstrip("@") for word in self.notes if word.startswith('@') and len(word) > 1]


#!/usr/bin/env python3
"""

# string_rules
    # title
    # description

    # contains string
    # equal to string
    # exists

# date rules
    # start date
    # due date
    # done date
    # stop_date
    # Manual date


    # exists
    # is same as
    # is later than
    # is earlier than

# Recurrence enabled
# recurrence interval
# recurrence increment
# recurrence weekdays
# recurrence stop_type
# recurrence stop number
# recurrence weekday_of_month

# and
# or
# not

"""
# default tags
# default tag behavior- description or title has tag

from uuid import uuid4


class Rule:
    def __init__(self):
        pass
        possible_attributes = [
            'title',
            'description',
            'start-date',
            'due-date',
            'done-date',
            'repeat-enabled',
        ]
        # all repeated attributes]
    # rules have 3 logic, attribute, result and comparison


class Tag:

    all_tags = []

    @staticmethod
    def get_all():
        return [tag for tag in Tag.all_tags]

    def __init__(self, parent=None):
        self.id = uuid4()
        self.name = ''
        self.colour = None
        self.priority = 0  # changes the sort ordering of the tag in a lists
        self.ruleset = None  # rulesets determine which tasks show up under which tags.
        self.parent = parent
        self.all_tags.append(self)

    @property
    def children(self):
        return [tag for tag in self.all_tags if tag.parent == self]

    def delete(self, delete_subtasks=False):
        for child in self.children:
            if delete_subtasks:
                child.delete(delete_subtasks=True)
            else:
                child.parent = None
        self.all_tags.remove(self)


# Built in Tags --------------------------------------------------------------------------------------------------------
all_tasks = Tag()
all_tasks.name = 'All Tasks'
all_tasks.ruleset = True


# built in tags
# untagged
# ruleset 1: description or title has tag


class TagManagerCore():
    def __init__(self, node_class=Tag):
        pass

    @property
    def tags(self):
        return [word.lstrip("@") for word in self.notes if word.startswith('@') and len(word) > 1]
# TODO.txt: Implement tag binding and table creation on storage change
