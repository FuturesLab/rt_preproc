from cleo.commands.command import Command
from cleo.helpers import argument
from runtime_preproc.parser.desugarer import Desugarer

class RunCommand(Command):
    name = "patch"
    description = "Patch a file to convert compile-time C preprocessor macros to runtime logic"
    arguments = [
        argument(
            "file",
            description="C file to patch",
            optional=False
        )
    ]
    options = [ ]

    def handle(self):
        file = self.argument("file")
        self.line(f"File: {file}")
        with open(file, mode="rb") as f:
            bytes = f.read()
            ds = Desugarer()
            tree = ds.parse(bytes)
            self.line("---- C FILE ----")
            self.line(tree.text.decode('utf8'))
            self.line("---- AST -------")
            self.line(tree.root_node.sexp())
