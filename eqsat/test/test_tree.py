from eqsat.tree import Node, ConstantNode, ArgumentNode

def test_node_has_children():
    t = Node('a', [])
    assert t.children == []

    t = Node('a', [1,2,3])
    assert t.children == [1,2,3]

def test_node_has_a_name():
    t = Node('a')
    assert t.name == 'a'

def test_constant_node():
    t = ConstantNode(1)
    assert t.value == 1

def test_argument_node():
    t = ArgumentNode(99)
    assert t.position == 99
