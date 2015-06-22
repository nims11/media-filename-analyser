from collections import defaultdict
class Trie(object):
    def __init__(self, key, parent=None):
        self.key = key
        self.count = 0
        self.num_successors = 0
        self.children = {}
        self.parent = parent
        self.votes = defaultdict(float)
        self.votes.update({'artist': 0, 'album': 0, 'disc': 0})

    def insert(self, lst):
        self.num_successors += 1
        if len(lst) == 0:
            self.count += 1
            return
        if lst[0] not in self.children:
            self.children[lst[0]] = Trie(lst[0], parent=self)
        self.children[lst[0]].insert(lst[1:])
    
    def query(self, lst):
        if len(lst) == 0:
            return self
        if lst[0] not in self.children:
            return None
        return self.children[lst[0]].query(lst[1:])
