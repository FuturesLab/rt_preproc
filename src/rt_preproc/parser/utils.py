from tree_sitter import Node
from rt_preproc.parser.ast import TreeSitterNode, type_name_to_class
from rt_preproc.parser.ast import *
from copy import copy

# Convert AST nodea to TreeSitterNode representation.

def reify(ast: Node) -> TreeSitterNode:
    new_node = type_name_to_class[ast.type]()
    new_node.base_node = ast
    new_node.children = []
    new_node.parent = None
    new_node.text = ""

    if isinstance(new_node, BinaryExpression) \
    or isinstance(new_node, AssignmentExpression) \
    or isinstance(new_node, InitDeclarator): 
        children = ast.children
    else:
        children = ast.named_children

    new_node.children = [reify(x) for x in children]

    return new_node


# Hacky way to recurse AST to get root node. 

def get_root_node(node: TreeSitterNode):
    if isinstance(node.parent, TranslationUnit):
        return node.parent
    
    return get_root_node(node.parent)


# Retrieve macro text for a given preproc node.

def get_macro(node: TreeSitterNode):
    
    # TODO: PreProcIf    

    if isinstance(node, PreprocIfdef):
        return node.children[0].text


# Remove a child node from its parent node.

def remove_child(child: TreeSitterNode, 
                 parent: TreeSitterNode):
    
    child.parent = None

    if hasattr(parent, "children") \
    and parent.children is not None:
        parent.children.remove(child)

    # If parent preproc block has no children left 
    # (i.e., its only child is a macro), remove it.

    if isinstance(parent, PreprocIfdef) \
    and isinstance(parent.children[-1], Identifier):
        remove_child(parent, parent.parent)
    
    return


# Move node to new destination, clearing the 
# previous parent (if necessary).

def move_node(node: TreeSitterNode, 
              dest: TreeSitterNode,
              pos: int):

    if hasattr(node, "parent") \
    and node in node.parent.children:
        remove_child(node, node.parent)

    dest.children.insert(pos, node)
    node.parent = dest

    return


# Move variable declarations.

def move_var_decl(decl: TreeSitterNode):
    assert(isinstance(decl, Declaration))

    # Initialized declarations.
    
    if hasattr(decl, "children") \
    and len(decl.children) > 1 \
    and isinstance(decl.children[1], InitDeclarator): 
        init_stmt = decl.children[1]
        var_type  = decl.children[0]
        var_name  = copy(init_stmt.children[0])

        # Move var name and type to a declaration statement.

        decl_stmt = Declaration()
        move_node(var_name, decl_stmt, 0)
        move_node(var_type, decl_stmt, 0)
        move_node(decl_stmt, decl.parent.parent, 0)

        # Move var name and init value to assignment expression.

        expr_stmt = ExpressionStatement()
        assn_expr = AssignmentExpression()
        assn_expr.children = copy(init_stmt.children)
        expr_stmt.text = ' '.join([child.text.decode('utf-8') \
            for child in assn_expr.children]).encode('utf-8')

        move_node(assn_expr, expr_stmt, 0)
        decl_loc = decl.parent.children.index(decl)
        move_node(expr_stmt, decl.parent, decl_loc)
        remove_child(decl, decl.parent)

        return
        
    # Uninitialized declaration.
    
    else: 
        move_node(decl, decl.parent.parent, 0)
    
    return


# Move any newly-declared functions or variables.

def move_decls(node: TreeSitterNode):
    for child in node.children:

        # Move function defintions to root node.

        if isinstance(child, FunctionDefinition) \
        or isinstance(child, FunctionDeclarator):
            move_node(child, get_root_node(child), 0)

        # Move var decls to the parent preproc block.

        if isinstance(child, Declaration):
            move_var_decl(child)

    return


# Rewrite a preprocessor block as an if statement.

def rewrite_as_if(node: TreeSitterNode):
    if hasattr(node, "children") and len(node.children) > 1:
        if_stmt = IfStatement()
        if_cond = ParenthesizedExpression()
        if_cond.text = ("\"%s\"".encode('utf-8') % get_macro(node))
        if_body = CompoundStatement()
        if_idx  = node.parent.children.index(node)

        move_node(if_body, if_stmt, 0)
        move_node(if_cond, if_stmt, 0)
        move_node(if_stmt, node.parent, if_idx)

        for (index,child) in enumerate(node.children[1:]):
            move_node(child, if_body, index)
    return

