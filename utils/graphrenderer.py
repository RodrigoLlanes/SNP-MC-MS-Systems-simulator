from collections import defaultdict
import re
from typing import Optional

import graphviz


class GraphRenderer:
    def __init__(self, name, comment=''):
        self.graph = graphviz.Digraph(name, comment=comment)

    def add_node(self, node: str, label=None, initial: bool = False, final: bool = False, node_label: bool = True):
        if label:
            label = re.sub('\n', '<BR/>', label)
        shape = 'none' if final else None
        self.graph.node(node, label, xlabel=node if node_label and not final else None, shape=shape)

        if initial:
            self.graph.node('', shape='none')
            self.graph.edge('', node)

    def add_edge(self, start: str, end: str, label: Optional[str] = None):
        self.graph.edge(start, end, label=f'({label})' if label else None)

    def render(self, path):
        self.graph.render(directory=path).replace('\\', '/')
