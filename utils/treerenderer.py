from interpreter.ast import *
from interpreter.token import TokenType
from utils.graphrenderer import GraphRenderer


class TreeRenderer(Visitor[str]):
    def __init__(self):
        self.gr = GraphRenderer('ParsedTree')
        self._last_id = 0

    @property
    def node(self):
        self._last_id += 1
        return str(self._last_id - 1)

    def visitRegexExpr(self, expr: Regex) -> str:
        node = self.node
        self.gr.add_node(node, label='regex', node_label=False)
        for e in expr.content:
            other = e.accept(self)
            self.gr.add_edge(node, other)
        return node

    def visitProductionExpr(self, expr: Production) -> str:
        node = self.node
        self.gr.add_node(node, label='production', node_label=False)
        self.gr.add_edge(node, expr.membrane.accept(self))
        self.gr.add_edge(node, expr.regex.accept(self))

        prod = self.node
        self.gr.add_node(prod, label='→', node_label=False)
        self.gr.add_edge(node, prod)

        self.gr.add_edge(prod, expr.consumed.accept(self))

        right = self.node
        self.gr.add_node(right, label='', node_label=False)
        self.gr.add_edge(prod, right)
        for send, channel in expr.channels:
            pair = self.node
            self.gr.add_node(pair, label='', node_label=False)
            self.gr.add_edge(right, pair)
            self.gr.add_edge(pair, send.accept(self))
            self.gr.add_edge(pair, channel.accept(self))
        return node

    def visitSinapsisExpr(self, expr: Sinapsis) -> str:
        node = self.node
        self.gr.add_node(node, label='sinapsis', node_label=False)
        self.gr.add_edge(node, expr.channel.accept(self))
        prod = self.node
        self.gr.add_node(prod, label='→', node_label=False)
        self.gr.add_edge(node, prod)
        self.gr.add_edge(prod, expr.left.accept(self))
        self.gr.add_edge(prod, expr.right.accept(self))
        return node

    def visitCallExpr(self, expr: Call) -> str:
        node = expr.identifier.accept(self)
        for param in expr.params:
            self.gr.add_edge(node, param.accept(self))
        return node

    def visitBinaryExpr(self, expr: Binary) -> str:
        node = self.node
        self.gr.add_node(node, label=expr.operator.lexeme, node_label=False)
        self.gr.add_edge(node, expr.left.accept(self))
        self.gr.add_edge(node, expr.right.accept(self))
        return node

    def visitFunctionExpr(self, expr: Function) -> str:
        node = self.node
        self.gr.add_node(node, label=f'{expr.identifier.lexeme} ({", ".join(p.lexeme for p in expr.parameters)})', node_label=False)
        for i in expr.instructions:
            self.gr.add_edge(node, i.accept(self))
        return node

    def visitStructExpr(self, expr: Struct) -> str:
        node = self.node
        self.gr.add_node(node, label='{}', node_label=False)
        for e in expr.content:
            self.gr.add_edge(node, e.accept(self))
        return node

    def visitIdentifierExpr(self, expr: Identifier) -> str:
        node = self.node
        self.gr.add_node(node, label=f'{expr.identifier.lexeme}', node_label=False)
        return node

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return expr.expression.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> str:
        node = self.node
        self.gr.add_node(node, label=str(expr.value), node_label=False)
        return node

    def visitUnaryExpr(self, expr: Unary) -> str:
        node = self.node
        if expr.operator.token_type == TokenType.OPEN_MEMBRANE:
            self.gr.add_node(node, label='[]', node_label=False)
            self.gr.add_edge(node, expr.right.accept(self))
        elif expr.operator.token_type == TokenType.OPEN_CHANNEL:
            self.gr.add_node(node, label='( )', node_label=False)
            self.gr.add_edge(node, expr.right.accept(self))
        else:
            self.gr.add_node(node, label=expr.operator.lexeme, node_label=False)
            self.gr.add_edge(node, expr.right.accept(self))
        return node
