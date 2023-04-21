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

    def ifdef_conds_query(self, tree: Tree) -> list[str]:
        # https://tree-sitter.github.io/tree-sitter/playground
        ifdef = C_LANGUAGE.query(
            """
        (preproc_ifdef
            (identifier) @cond
            (_) @contents
        )
        """
        )
        caps = ifdef.captures(tree.root_node)
        conds = [node.text.decode("utf8") for node, name in caps if name == "cond"]

        # example of funcs for conds
        (
            f"int rt_{cond}() {{" f' return getenv("{cond}") != NULL;' f"}}"
            for cond in conds
        )

        # f"if ({new_name}) {{"

        return conds
