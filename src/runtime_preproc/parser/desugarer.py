from tree_sitter import Parser, Tree
from runtime_preproc.parser import C_LANGUAGE
class Desugarer:
    def __init__(self):
        parser = Parser()
        parser.set_language(C_LANGUAGE)
        self.parser = parser

    def parse(self, bytes) -> Tree:
        return self.parser.parse(bytes)
    
    def ifdef_conds_query(self, tree: Tree) -> list[str]:
        # https://tree-sitter.github.io/tree-sitter/playground
        ifdef = C_LANGUAGE.query("""
        (preproc_ifdef 
            (identifier) @cond
            (_) @contents
        )
        """)
        caps = ifdef.captures(tree.root_node)
        conds = [node.text.decode('utf8') for node, name in caps if name == "cond"]
        
        funcs = (
f"int rt_{cond}() {{"
f" return getenv(\"{cond}\") != NULL;"
f"}}"
      for cond in conds)

        # f"if ({new_name}) {{"

        return conds
