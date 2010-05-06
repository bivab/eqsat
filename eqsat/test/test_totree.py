from pypy.translator.interactive import Translation
from eqsat.totree import transform_graph
class TestTransformation(object):
    def make_graph(self, f, arguments):
        t = Translation(f)
        t.rtype(arguments)
        return t.context.graphs[0]

    def test_very_simple(self):
        def f(x):
            return x + 1
        graph = self.make_graph(f, [int])
        tree = transform_graph(graph)
        assert tree.name == "int_add"
        assert len(tree.children) == 2
        assert tree.children[0].position == 0
        assert tree.children[1].value.value == 1
