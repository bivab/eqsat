from pypy.translator.backendopt import support
from pypy.objspace.flow import model as flowmodel

from eqsat.tree import ArgumentNode, Node, ConstantNode

def transform_graph(graph):
    t = Transformator(graph)
    return t.transform()

class Transformator(object):

    def __init__(self, graph):
        self.graph = graph
        self.startblock = graph.startblock
        self.vartonode = {}

    def transform(self):
        assert not support.find_loop_blocks(self.graph)
        for i,var in enumerate(self.startblock.inputargs):
            self.vartonode[var] = ArgumentNode(i)
        for op in self.startblock.operations:
            tree = self.transform_op(op)
            self.vartonode[op.result] = tree
        assert len(self.startblock.exits) == 1
        assert self.startblock.exits[0].target is self.graph.returnblock
        return self.get_node(self.startblock.exits[0].args[0])

    def transform_op(self, op):
        children = [self.get_node(arg) for arg in op.args]
        return Node(op.opname, children)

    def get_node(self, varorconst):
        try:
            return self.vartonode[varorconst]
        except KeyError:
            pass
        if isinstance(varorconst, flowmodel.Constant):
            result = ConstantNode(varorconst)
            self.vartonode[varorconst] = result
            return result
        assert 0, "variable should be in dictionary already"
