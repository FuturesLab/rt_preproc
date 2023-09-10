from tree_sitter import Node
from rt_preproc.parser import ast
from copy import copy

# Hacky way to recurse AST to get root node.
def get_root_node(node: ast.AstNode):
    if isinstance(node.parent, ast.TranslationUnit):
        return node.parent

    return get_root_node(node.parent)


# Retrieve macro text for a given preproc node.


def get_macro(node: ast.AstNode):
    # TODO: PreProcIf

    if isinstance(node, ast.PreprocIfdef):
        return node.children[0].text


# Remove a child node from its parent node.


def remove_child(child: ast.AstNode, parent: ast.AstNode):
    child.parent = None

    if hasattr(parent, "children") and parent.children is not None:
        parent.children.remove(child)

    # If parent preproc block has no children left
    # (i.e., its only child is a macro), remove it.

    if isinstance(parent, ast.PreprocIfdef) and isinstance(
        parent.children[-1], ast.Identifier
    ):
        remove_child(parent, parent.parent)

    return


# Move node to new destination, clearing the
# previous parent (if necessary).


def move_node(node: ast.AstNode, dest: ast.AstNode, pos: int):
    if hasattr(node, "parent") and node in node.parent.children:
        remove_child(node, node.parent)

    dest.children.insert(pos, node)
    node.parent = dest

    return


# Move variable declarations.


def move_var_decl(decl: ast.AstNode):
    assert isinstance(decl, ast.Declaration)

    # Initialized declarations.

    if (
        hasattr(decl, "children")
        and len(decl.children) > 1
        and isinstance(decl.children[1], ast.InitDeclarator)
    ):
        init_stmt = decl.children[1]
        var_type = decl.children[0]
        var_name = copy(init_stmt.children[0])

        # Move var name and type to a declaration statement.

        decl_stmt = ast.Declaration()
        move_node(var_name, decl_stmt, 0)
        move_node(var_type, decl_stmt, 0)
        move_node(decl_stmt, decl.parent.parent, 0)

        # Move var name and init value to assignment expression.

        expr_stmt = ast.ExpressionStatement()
        assn_expr = ast.AssignmentExpression()
        assn_expr.children = copy(init_stmt.children)
        expr_stmt.text = " ".join(
            [child.text.decode("utf-8") for child in assn_expr.children]
        ).encode("utf-8")

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


def move_decls(node: ast.AstNode):
    for child in copy(node.children):
        if isinstance(child, ast.FunctionDefinition):
            move_node(child, get_root_node(child), 0)
        if isinstance(child, ast.FunctionDeclarator):
            move_node(child, get_root_node(child), 0)
        if isinstance(child, ast.Declaration):
            move_var_decl(child)
    return


# Rewrite a preprocessor block as an if statement.


def rewrite_as_if(node: ast.AstNode):
    if hasattr(node, "children") and len(node.children) > 1:
        if_stmt = ast.IfStatement()
        if_cond = ast.ParenthesizedExpression()
        if_cond.text = '"%s"'.encode("utf-8") % get_macro(node)
        if_body = ast.CompoundStatement()
        if_idx = node.parent.children.index(node)

        move_node(if_body, if_stmt, 0)
        move_node(if_cond, if_stmt, 0)
        move_node(if_stmt, node.parent, if_idx)

        for child_idx, child in enumerate(copy(node.children[1:])):
            move_node(child, if_body, child_idx)
    return
