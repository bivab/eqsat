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
        self.seenblocks = set()

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
        if merged_dict is None:
            return
        for op in block.operations:
            tree = self.transform_op(op)
            self.vartonode[op.result] = tree
        self.seenblocks.add(block)
        self.transform_links(block, merged_dict)

    def transform_links(self, block, block_dict):
        if len(block.exits) > 1:
            for exit in block.exits:
                d = block_dict.copy()
                d[block.exitswitch] = exit.exitcase
                self.link_to_conditions[exit] = d
        else:
            self.link_to_conditions[block.exits[0]] = block_dict
        for exit in block.exits:
            self.transform_block(exit.target)

    def merge_incoming_links(self, block):
        incoming = self.entrymap[block]
        for l in incoming:
            if l.prevblock is not None and l.prevblock not in self.seenblocks:
                return None
        dicts = [self.link_to_conditions.get(x, {}) for x in incoming]
        if len(dicts) == 2:
            for d in dicts:
                assert len(d) <= 1
            d1, d2 = dicts
            k1 = d1.keys()[0]
            assert d1[k1] == (not d2[k1])
            node = self.get_node(k1)
            args = []
            for a1, b1, c in zip(incoming[0].args, incoming[1].args, block.inputargs):
                a1node = self.get_node(a1)
                b1node = self.get_node(b1)
                if not d1[k1]:
                    a1node, b1node = b1node, a1node
                self.vartonode[c] = Node('tree_if', [node, a1node, b1node])
        else:
            assert len(dicts) == 1
            args = incoming[0].args
            for arg1, arg2 in zip(args, block.inputargs):
                self.vartonode[arg2] = self.get_node(arg1)
            return dicts[0]
        return {}

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
