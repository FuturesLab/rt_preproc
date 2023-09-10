from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.ast import AstNode
from rt_preproc.parser.parser import Parser
from rt_preproc.visitors.print import PrintCtx, PrintVisitor


class PrintCmd(Command):
    name = "print"
    description = "Print a C file from its AST."
    arguments = [argument("file", description="C file to print", optional=False)]
    options = []

    def handle(self):
        file = self.argument("file")
        self.line(f"File: {file}")
        with open(file, mode="rb") as f:
            bytes = f.read()
            ds = Parser()
            tree = ds.parse(bytes)
            root_node = AstNode.reify(tree.root_node)
            visitor = PrintVisitor()
            root_node.accept(visitor, PrintCtx())
