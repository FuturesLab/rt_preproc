from typing import Optional, List, Any, Self, Set
import rt_preproc.parser.ast as ast
from collections import defaultdict

class Macro:
    def __init__(self, name: str, type: str, def_cond: bool = False):
        self.name = name
        self.type = type
        self.def_cond = def_cond

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Macro):
            return False
        return self.name == other.name and self.type == other.type and self.def_cond == other.def_cond

    def __hash__(self) -> int:
        return hash((self.name, self.type, self.def_cond))

class FuncDecl:
    def __init__(self, fn_decl: ast.FunctionDeclarator, macro_set: set[Macro]):
        self.fn_decl = fn_decl
        self.macro_set = macro_set

class VarIdent:
    def __init__(self, name: str, macro_set: set[Macro], orig_name: Optional[str] = None):
        self.name = name
        self.macro_set = macro_set
        self.orig_name = orig_name

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
    
class DefDecl:
    def __init__(self, name: str, val: str, macro_set: set[Macro], orig_name: str = None):
        self.name = name
        self.val = val
        self.macro_set = macro_set
        self.orig_name = orig_name or name

    def convert_to_ast(self) -> ast.AstNode:
        new_node = ast.Custom(f"#define {self.name} {self.val}\n")
        return new_node

class DefFnDecl:
    def __init__(self, name: str, params: ast.PreprocParams, val: str, macro_set: set[Macro], orig_name: str = None):
        self.name = name
        self.params = params
        self.val = val
        self.macro_set = macro_set
        self.orig_name = orig_name or name

    def convert_to_ast(self) -> ast.AstNode:
        new_node = ast.Custom(f"#define {self.name}{str(self.params)} {self.val}\n")
        return new_node

class MoveUpMsg:
    def __init__(
        self,
        node: Optional[ast.AstNode] = None,
        move_up_nodes: List[ast.AstNode] = [],
        var_idents: Set[str] = set(), # these are variable identifers that are compile-time variable
    ) -> None:
        self.node = node

        self.move_ups: List[ast.AstNode] = []
        self.move_ups.extend(move_up_nodes)
        # if I do self.var_idents = var_idents instead, then the var_idents will be shared between all instances (we don't want that)
        # same for move_ups
        self.var_idents: Set[str] = set()
        self.var_idents.update(var_idents)
