class Base(object):

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

class Node(Base):
    def __init__(self, name, children=None):
        self.name = name
        self.children = children

class ConstantNode(Base):
    def __init__(self, value):
        self.value = value

class ArgumentNode(Base):
    def __init__(self, pos):
        self.position = pos
