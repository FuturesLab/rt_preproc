from tree_sitter import Node
from rt_preproc.parser.ast import TreeSitterNode, type_name_to_class


def reify(ast: Node) -> TreeSitterNode:
    new_node = type_name_to_class[ast.type]()
    new_node.base_node = ast
    new_node.children = []
    for child in ast.named_children:
        new_node.children.append(reify(child))
    return new_node
