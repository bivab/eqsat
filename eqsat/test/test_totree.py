from eqsat.totree import transform_graph
from eqsat.tree import ArgumentNode, Node, ConstantNode

from pypy.objspace.flow import model as flowmodel
from pypy.translator.backendopt import support
from pypy.translator.interactive import Translation

class TestTransformation(object):
    def make_graph(self, f, arguments):
        t = Translation(f)
        t.rtype(arguments)
        return t.context.graphs[0]

    def test_very_simple_alias_add_1(self):
        def f(x):
            return x + 1
        tree = self.make_tree(f, [int])
        assert tree.name == "int_add"
        assert len(tree.children) == 2
        assert tree.children[0].position == 0
        assert tree.children[1].value.value == 1

    def test_slightly_less_simple(self):
        def f(x, y):
            z = x * y + 1
            return z + z + x
        tree = self.make_tree(f, [int, int])
        a0 = ArgumentNode(0)
        a1 = ArgumentNode(1)
        m  = Node('int_mul', [a0, a1])
        one = ConstantNode(flowmodel.Constant(1))
        add1 = Node('int_add', [m, one])
        add2 = Node('int_add', [add1, add1])
        assert tree == Node('int_add', [add2, a0])
        tree.view()

    def test_tree_with_if(self):
        def f(x, y, z):
            if x:
                return y + 1
            if y:
                return z + 1
            else:
                return 5
        tree = self.make_tree(f, [int, int, int], True)
        assert tree == Node('tree_if', [
                        Node('int_is_true', [ArgumentNode(0)]),
                        ArgumentNode(1), ArgumentNode(2)])

    def test_tree_simple_if(self):
        def f(a,b):
            if a:
                return a
            else:
                return b
        tree = self.make_tree(f, [int, int], False)
        assert tree == Node('tree_if', [
                        Node('int_is_true', [ArgumentNode(0)]),
                        ArgumentNode(0), ArgumentNode(1)])

    def make_tree(self, f, args, show=False):
        graph = self.make_graph(f, args)
        if show:
            graph.show()
        return transform_graph(graph)


