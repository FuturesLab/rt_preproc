from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.ast import TreeSitterNode
from rt_preproc.parser.parser import Parser
from rt_preproc.parser.utils import reify
from rt_preproc.visitors.transform import TransformCtx, TransformVisitor
from rt_preproc.visitors.print import PrintCtx, PrintVisitor


class PatchCmd(Command):
    name = "patch"
    description = (
        "Patch a file to convert compile-time C preprocessor macros to runtime logic"
    )
    arguments = [argument("file", description="C file to patch", optional=False)]
    options = []

    def handle(self):
        file = self.argument("file")
        self.line(f"File: {file}")
        with open(file, mode="rb") as f:
            bytes  = f.read()
            ds     = Parser()
            tree   = ds.parse(bytes)
            nodes  = ds.query(tree)

            root_node: TreeSitterNode = reify(tree.root_node)

            self.line("\n---- ORIGINAL C SOURCE ----")
            printer = PrintVisitor()
            root_node.accept(printer, PrintCtx()) 

            visitor = TransformVisitor()
            root_node.accept(visitor, TransformCtx())

            self.line("\n---- PATCHED C SOURCE ----")
            printer = PrintVisitor()
            root_node.accept(printer, PrintCtx())


