from tree_sitter import Node
from rt_preproc.parser.ast import TreeSitterNode, type_name_to_class


def reify(ast: Node) -> TreeSitterNode:
    new_node = type_name_to_class[ast.type]()
    new_node.base_node = ast
    new_node.children = []
    new_node.parent = None

    #if ast.parent is not None:
        #new_node.parent = type_name_to_class[ast.parent.type]()
        #new_node.parent = TreeSitterNode(ast.parent)

    #if ast.next_sibling is not None:
    #    new_node.sibling = reify(ast.next_sibling)

    for child in ast.named_children:
        new_node.children.append(reify(child))

    return new_node
