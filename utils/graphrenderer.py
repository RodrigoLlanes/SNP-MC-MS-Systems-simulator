from collections import defaultdict
import re
import graphviz


class GraphRenderer:
    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)

    def add_node(self, node: str, label=None):
        if label is None:
            label = str(node)
        self.nodes[node] = label

    def add_edge(self, start: str, end: str, label=None):
        self.edges[start].append((end, label))

    def render(self, path, name, comment=''):
        dot = graphviz.Digraph(name, comment=comment)
        for node, label in self.nodes.items():
            label = re.sub('\n', '<BR/>', label)
            dot.node(node, label)
        for start, edges in self.edges.items():
            for end, label in edges:
                if label is None:
                    dot.edge(start, end)
                else:
                    dot.edge(start, end, label=label)

        # print(dot.source)
        print(dot.render(directory=path).replace('\\', '/'))
