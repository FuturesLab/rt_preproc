from cleo.commands.command import Command
from cleo.helpers import argument, option
from rt_preproc.parser.ast import AstNode
from rt_preproc.parser.parser import Parser
from rt_preproc.visitors.transform import TransformCtx, TransformVisitor
from rt_preproc.visitors.print import PrintCtx, PrintVisitor


class PatchCmd(Command):
    name = "patch"
    description = (
        "Patch a file to convert compile-time C preprocessor macros to runtime logic"
    )
    arguments = [argument("file", description="C file to patch", optional=False)]
    options = [option("output", "o", description="Output file to write to", flag=False)]

    def runPatch(self, file: str, just_output: bool = False, output_file: str = None):
        if not just_output:
            self.line(f"File: {file}")
        with open(file, mode="rb") as f:
            bytes = f.read()
            ds = Parser()
            tree = ds.parse(bytes)

            root_node = AstNode.reify(tree.root_node)

            if not just_output:
                self.line("\n---- ORIGINAL C SOURCE ----")
                printer = PrintVisitor()
                root_node.accept(printer, PrintCtx())

            visitor = TransformVisitor()
            root_node.accept(visitor, TransformCtx())

            if not just_output:
                self.line("\n---- PATCHED C SOURCE ----")
            printer = PrintVisitor(output_file=output_file)
            root_node.accept(printer, PrintCtx())

    def handle(self):
        opt = self.option("output")
        self.runPatch(self.argument("file"), output_file=opt)
