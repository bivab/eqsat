
class Base(object):

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self == other

    def view(self):
        import py
        from dotviewer import graphclient
        content = ["digraph G{"]
        seen = set()
        content.extend(self._dot(seen))
        content.append("}")
        p = py.path.local.make_numbered_dir("eqsat-").join("temp.dot")
        p.write("\n".join(content))
        graphclient.display_dot_file(str(p))

class Node(Base):
    def __init__(self, name, children=None):
        self.name = name
        self.children = children

    def _dot(self, seen):
        if self in seen:
            return
        seen.add(self)
        yield '%s [label="%s", shape=box]' % (id(self), self.name)
        for i, child in enumerate(self.children):
            for line in child._dot(seen):
                yield line
            yield '%s -> %s [label=%s]'  % (id(self), id(child), i)

class ConstantNode(Base):
    def __init__(self, value):
        self.value = value

    def _dot(self, seen):
        if self in seen:
            return
        seen.add(self)
        yield '%s [label="%s"]' % (id(self), self.value)

class ArgumentNode(Base):
    def __init__(self, pos):
        self.position = pos

    def _dot(self, seen):
        if self in seen:
            return
        seen.add(self)
        yield '%s [label="<arg %s>"]' % (id(self), self.position)
