from cleo.commands.command import Command
from cleo.helpers import argument
from rt_preproc.parser.parser import Parser


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

            # Read file into f and perform parsing.

            bytes     = f.read()
            ds        = Parser()
            tree      = ds.parse(bytes)
            tree_text = tree.text.decode("utf8")
            nodes     = ds.query(tree)

            # Set up a "stack" (list) to support parsing.

            seen_blks = []

            # Split tree into lines and perform patching.

            tree_split = tree_text.split('\n')
            (prefix_line, prefix_offset) = (0,0)
            (suffix_line, suffix_offset) = (0,0)

            # Go through the tree node-by-node, looking for blocks...

            for (node,name) in nodes:
                print(seen_blks)

                # If hit "block, grab its bounds and append to our list.

                if name == "block": 
                    seen_blks.append(node)
                    (prefix_line, prefix_offset) = node.start_point
                    (suffix_line, suffix_offset) = node.end_point

                # If hit "macro", rewrite the block as a conditional.
                
                if name == "macro" and node.parent == seen_blks[-1]:
                    macro_text = node.text.decode("utf8")

                    tree_split[prefix_line] = "%sif(%s){" % \
                        (' '*prefix_offset, macro_text)

                    tree_split[suffix_line] = "%s}" % \
                        (' '*prefix_offset)

            tree_done = '\n'.join(tree_split)

            self.line("---- INPUT C FILE ----")
            self.line(tree_text)

            self.line("---- OUTPUT C FILE ----")
            self.line(tree_done)


