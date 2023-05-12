from tree_sitter import Node
from rt_preproc.parser.ast import TreeSitterNode, type_name_to_class
from rt_preproc.parser.ast import *

def reify(ast: Node) -> TreeSitterNode:
    new_node = type_name_to_class[ast.type]()
    new_node.base_node = ast
    new_node.children = []
    new_node.parent = None
    new_node.text = ""

    #for child in ast.named_children:
    #    new_node.children.append(reify(child))

    if isinstance(new_node, BinaryExpression) \
    or isinstance(new_node, InitDeclarator): 
        children = ast.children
    else:
        children = ast.named_children

    new_node.children = [reify(x) for x in children]

    return new_node
