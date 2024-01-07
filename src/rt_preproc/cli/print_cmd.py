from cleo.commands.command import Command
from cleo.helpers import argument, option
from rt_preproc.parser.ast import AstNode
from rt_preproc.parser.parser import Parser
from rt_preproc.visitors.print import PrintCtx, PrintVisitor


class PrintCmd(Command):
    name = "print"
    description = "Print a C file from its AST."
    arguments = [
        argument("file", description="C file to print", optional=False),
        argument(
            "output",
            description="Output file to write to",
            optional=True,
        ),
    ]
    options = [
        option(
            "fmt",
            description="Run astyle on the output",
        )
    ]

    def handle(self):
        file = self.argument("file")
        self.line(f"File: {file}")
        with open(file, mode="rb") as f:
            bytes = f.read()
            ds = Parser()
            tree = ds.parse(bytes)
            root_node = AstNode.reify(tree.root_node)
            visitor = PrintVisitor(
                output_file=self.argument("output"), use_astyle=self.option("fmt")
            )
            root_node.accept(visitor, PrintCtx())
