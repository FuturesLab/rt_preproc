from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.ast import TreeSitterNode
from rt_preproc.parser.parser import Parser
from rt_preproc.parser.utils import reify
from rt_preproc.visitors.graphviz import GraphVizCtx, GraphVizVisitor


class GraphvizCmd(Command):
    name = "graphviz"
    description = "Graph the AST of a file using graphviz"
    arguments = [argument("file", description="C file to graph", optional=False)]
    options = []

    def handle(self):
        file = self.argument("file")
        with open(file, mode="rb") as f:
            bytes = f.read()
            ds = Parser()
            tree = ds.parse(bytes)
            root_node: TreeSitterNode = reify(tree.root_node)
            visitor = GraphVizVisitor()
            root_node.accept(visitor, GraphVizCtx())
