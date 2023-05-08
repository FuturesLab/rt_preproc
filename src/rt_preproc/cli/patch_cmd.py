from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.parser import Parser

# Function to insert "getenv(macro)" stubs.

def add_stubs(tree, macros):
    for macro in set(macros):
        tree.insert(0, "/* Variability Stub */\nint rt_%s() {\
            \n  return getenv(\"%s\") != NULL;\n}\n" % (macro, macro))

    tree.insert(0,"#include <stdlib.h>\n")
    return tree

# Main class...

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

        # Read file into f and perform parsing.
        
        with open(file, mode="rb") as f:
            bytes  = f.read()
            ds     = Parser()
            tree   = ds.parse(bytes)
            nodes  = ds.query(tree)
            tree   = tree.text.decode("utf8").split('\n') 
            seen   = []
            macros = []

            self.line("---- INPUT C FILE ----")
            self.line('\n'.join(tree))

            # Visit nodes and process accordingly...

            for (node, name) in nodes:
                if name == "block": 

                    # Extract macro from first child ('identifier')...

                    macro = node.children[1].text.decode('utf-8')
                    macros.append(macro)

                    # Convert to conditional based on bounds and macro...

                    (start,end) = (node.start_point, node.end_point)
                    tree[start[0]] = "%sif(rt_%s()){" % (' '*start[1], macro)
                    tree[end[0]]   = "%s}" % (' '*start[1])

            tree = add_stubs(tree, macros) # Add helper stubs...

            # Done!

            self.line("---- OUTPUT C FILE ----")
            self.line('\n'.join(tree))


