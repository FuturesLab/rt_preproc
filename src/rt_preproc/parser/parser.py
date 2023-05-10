from tree_sitter import Parser as TSParser, Tree
from rt_preproc.parser import C_LANGUAGE


class Parser:
    def __init__(self):
        parser = TSParser()
        parser.set_language(C_LANGUAGE)
        self.parser = parser

    def parse(self, bytes) -> Tree:
        tree = self.parser.parse(bytes)
        return tree

    def query(self, tree: Tree) -> list[str]:
        query = """
            (preproc_ifdef)     @block
            (preproc_ifdef   (
                (identifier)    @macro
                (_)             @contents
            ))

            (preproc_if)        @block
            (preproc_if   (
                (identifier)    @macro
                (_)             @contents
            ))
        """

        captures = C_LANGUAGE.query(query).captures(tree.root_node)

        return captures
