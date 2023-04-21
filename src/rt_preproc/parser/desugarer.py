from tree_sitter import Parser, Tree, Node
from rt_preproc.parser import C_LANGUAGE
from rt_preproc.parser.ast import TreeSitterNode, type_name_to_class
from tree_sitter_types.parser import parse_node

from rt_preproc.visitors.graphviz import GraphVizCtx, GraphVizVisitor


class Desugarer:
    def __init__(self):
        parser = Parser()
        parser.set_language(C_LANGUAGE)
        self.parser = parser

    @staticmethod
    def reify(ast: Node) -> TreeSitterNode:
        new_node = type_name_to_class[ast.type]()
        new_node.base_node = ast
        new_node.children = []
        for child in ast.named_children:
            new_node.children.append(Desugarer.reify(child))
        return new_node

    def parse(self, bytes) -> Tree:
        tree = self.parser.parse(bytes)
        root_node: TreeSitterNode = self.reify(tree.root_node)

        visitor = GraphVizVisitor()
        print("----")
        root_node.accept(visitor, GraphVizCtx())
        print("----")
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
