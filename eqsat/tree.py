class Node(object):
    def __init__(self, name, children=None):
        self.name = name
        self.children = children

class ConstantNode(object):
    def __init__(self, value):
        self.value = value

class ArgumentNode(object):
    def __init__(self, pos):
        self.position = pos
