from typing import Optional, List, Any, Self
import rt_preproc.parser.ast as ast
from collections import defaultdict

class Macro:
    def __init__(self, name: str, type: str, def_cond: bool = False):
        self.name = name
        self.type = type
        self.def_cond = def_cond


class FuncDecl:
    def __init__(self, fn_decl: ast.FunctionDeclarator, macro_set: set[Macro]):
        self.fn_decl = fn_decl
        self.macro_set = macro_set


class VarDecl:
    def __init__(
        self, name: str, type: str, val: Optional[ast.AstNode], macro_set: set[Macro]
    ):
        self.name = name
        self.type = type
        self.val = val
        self.macro_set = macro_set

    def convert_to_ast(self, var_decls: dict[str, List[Self]]) -> ast.AstNode:
        name = self.name
        if (len(var_decls[self.name]) > 1):
            name = self.name + "_" + str(len(var_decls[self.name]))
        new_node = ast.Declaration()
        if self.val is None:
            new_node.children = [
                ast.TypeIdentifier(self.type),
                ast.Whitespace(" "),
                ast.Identifier(name),
                ast.Custom(";"),
            ]
            return new_node
        new_node.children = [
            ast.TypeIdentifier(self.type),
            ast.Whitespace(" "),
            ast.Identifier(name),
            ast.Whitespace(" "),
            ast.Custom("="),
            ast.Whitespace(" "),
            self.val,
            ast.Custom(";"),
        ]
        return new_node



class MoveUpMsg:
    def __init__(
        self,
        node: Optional[ast.AstNode] = None,
        move_up_nodes: List[ast.AstNode] = [],
        var_decls_up: dict[str, List[VarDecl]] = defaultdict(list),
    ) -> None:
        self.node = node
        self.move_up: List[ast.AstNode] = []
        self.var_decls_up = var_decls_up
        self.move_up.extend(move_up_nodes)
