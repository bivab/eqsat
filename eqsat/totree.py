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
        self.returnblock = graph.returnblock
        self.vartonode = {}
        self.link_to_conditions = {}
        self.entrymap = flowmodel.mkentrymap(graph)

    def transform(self):
        assert not support.find_loop_blocks(self.graph)
        for i,var in enumerate(self.startblock.inputargs):
            self.vartonode[var] = ArgumentNode(i)
        self.transform_block(self.startblock)
        return self.get_node(self.returnblock.inputargs[0])

    def transform_op(self, op):
        children = [self.get_node(arg) for arg in op.args]
        return Node(op.opname, children)

    def transform_block(self, block):
        merged_dict = self.merge_incoming_links(block)
        for op in block.operations:
            tree = self.transform_op(op)
            self.vartonode[op.result] = tree
        self.transform_links(block, merged_dict)

    def transform_links(self, block, block_dict):
        if len(block.exits) > 1:
            for exit in block.exits:
                d = block_dict.copy()
                d[block.exitswitch] = exit.exitcase
                self.link_to_conditions[exit] = d

    def merge_incoming_links(self, block):
        incoming = self.entrymap[block]
        dicts = [self.link_to_conditions[x] for x in incoming]
        dicts.sort(key=lambda x: len(x))
        key_count = {}
        # select key with the least occurences in the dictionary

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
