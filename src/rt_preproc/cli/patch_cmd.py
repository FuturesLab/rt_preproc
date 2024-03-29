from cleo.commands.command import Command
from cleo.helpers import argument, option
from rt_preproc.parser.ast import AstNode
from rt_preproc.parser.parser import Parser
from rt_preproc.visitors.patch.patch import PatchCtx, PatchVisitor
from rt_preproc.visitors.print import PrintCtx, PrintVisitor


class PatchCmd(Command):
    name = "patch"
    description = (
        "Patch a file to convert compile-time C preprocessor macros to runtime logic"
    )
    arguments = [argument("file", description="C file to patch", optional=False)]
    options = [
        option("output", "o", description="Output file to write to", flag=False),
        option(
            "fmt",
            "f",
            description="Run astyle on the output",
        ),
        option(
            "just_output",
            "j",
            description="Just output the patched file",
        ),
    ]

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

            visitor = PatchVisitor()
            root_node.accept(visitor, PatchCtx())

            if not just_output:
                self.line("\n---- PATCHED C SOURCE ----")
            printer = PrintVisitor(output_file=output_file, use_astyle=self.option("fmt"))
            root_node.accept(printer, PrintCtx())

    def handle(self):
        opt = self.option("output")
        self.runPatch(
            self.argument("file"),
            just_output=self.option("just_output"),
            output_file=opt,
        )
