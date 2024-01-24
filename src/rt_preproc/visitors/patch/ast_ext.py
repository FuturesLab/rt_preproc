import rt_preproc.parser.ast as ast
import rt_preproc.visitors.patch.data as data

class Marker(ast.AstNode):
    field_names = []
    children: None

    def __init__(self) -> None:
        super().__init__()

class VariableUsageMarker(Marker):
    field_names = []
    children: None

    def __init__(self, variable: ast.Declaration, macro_set: set[data.Macro]) -> None:
        super().__init__()
        self.variable = variable
        self.macro_set = macro_set

class VariableDeclarationMarker(Marker):
    field_names = []
    children: None
    var_decl: data.VarDecl

    def __init__(self, var_decl: data.VarDecl) -> None:
        super().__init__()
        self.var_decl = var_decl

class PreprocDefinitionMarker(Marker):
    field_names = []
    children: None
    def_decl: data.DefDecl

    def __init__(self, def_decl: data.DefDecl) -> None:
        super().__init__()
        self.def_decl = def_decl