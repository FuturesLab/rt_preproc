from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.parser import Parser

# Insert "getenv(macro)" stubs.

def add_macro_stubs(tree, macros):
    for macro in set(macros):
        tree.insert(0, "// VarFuzz: begin macro stub\nint rt_%s() {\
            \n  return getenv(\"%s\") != NULL;\n}\n// VarFuzz: end macro stub\n" % (macro, macro))

    tree.insert(0,"#include <stdlib.h>\n")
    return tree

# Unwrap macro-declared functions.

def unwrap_func_decl(tree, block, child):
    tree[block.start_point[0]] = "// VarFuzz: begin function unwrap"
    tree[block.end_point[0]]   = "// VarFuzz: end function unwrap"

    for (i,line) in enumerate(child.text.decode('utf-8').split('\n')):
        tree[child.start_point[0]+i] = line
    
    tree[child.end_point[0]] = "}"

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

            for (block, name) in nodes:
                if name == "block": 
                    (start, end) = (block.start_point, block.end_point)

                    # Extract macro from first child ('identifier')...

                    macro = block.children[1].text.decode('utf-8')
                    macros.append(macro)

                    # Naively rewrite every block as a conditional...

                    tree[block.start_point[0]] = "%sif(rt_%s()){" % (' '*block.start_point[1], macro)
                    tree[block.end_point[0]]   = "%s}" % (' '*block.start_point[1])

                    # Rewrite block that should not be conditionals.
                    # Examples: blocks with func or var declarations. 

                    for child in block.children[1:]:
                        if child.type == "function_definition":
                            tree = unwrap_func_decl(tree, block, child)

            tree = add_macro_stubs(tree, macros) # Add helper stubs...

            # Done!

            self.line("---- OUTPUT C FILE ----")
            self.line('\n'.join(tree))


