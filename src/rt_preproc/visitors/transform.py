from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from html import escape


class TransformCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.TreeSitterNode] = None) -> None:
        self.parent = parent


class TransformVisitor(IVisitor):
    """Visitor for performing variability transformations on AST nodes."""

    def __init__(self) -> None:
        self.buf = ""
        self.seen = []

    def visit_children(
        self, node: ast.TreeSitterNode, ctx: TransformCtx, label: str = None
    ) -> list[Any]:

        if hasattr(node, "children") and node.children is not None:
            for child in node.children:
                child.parent = node
                if hasattr(child, "base_node"): child.text = child.base_node.text
                child.accept(self, TransformCtx(parent=node))    
            return
        return

    """ Hacky way to recurse AST to get root node. """

    def get_root_node(self, node: ast.TreeSitterNode):
        if isinstance(node.parent, ast.TranslationUnit):
            return node.parent
        return self.get_root_node(node.parent)

    """ Retrieve the macro string for a preproc node. """

    def get_pp_macro(self, pp_node: ast.TreeSitterNode):
        if isinstance(pp_node, ast.PreprocIfdef):
            return pp_node.children[0].text

    """ Unlinks a child node from its parent node. """

    def remove_child(self, child: ast.TreeSitterNode, 
                           parent: ast.TreeSitterNode, 
                           ctx: TransformCtx):
        parent.children.remove(child)
        child.parent = None
        if isinstance(parent, ast.PreprocIfdef) \
        and isinstance(parent.children[-1], ast.Identifier):
            self.remove_child(parent, parent.parent, ctx)
        return

    """ Move a node to a desired destination. """

    def move_node(self, node: ast.TreeSitterNode, 
                        dest: ast.TreeSitterNode,
                        pos: int, 
                        ctx: TransformCtx):
        if node.parent and node in node.parent.children:
            self.remove_child(node, node.parent, ctx)
        dest.children.insert(pos, node)
        node.parent = dest
        return

    """ Insert IF statement before parent preproc block. """

    def move_to_if(self, node: ast.TreeSitterNode,
                         ctx: TransformCtx):

        old_idx = node.parent.parent.children.index(node.parent)
        old_loc = node.parent.parent

        macro = self.get_pp_macro(node.parent)
        self.remove_child(node, node.parent, ctx) 

        new_if = ast.IfStatement() # "if ..."
        new_if.children = []
        new_if.parent = None

        new_pe = ast.ParenthesizedExpression() # "if (FOO)..."
        new_pe.text = ("\"%s\"".encode('utf-8')) % macro
        new_pe.children = []
        new_pe.parent = None

        self.move_node(new_pe, new_if, 0, ctx)
        self.move_node(node, new_if, 1, ctx)
        self.move_node(new_if, old_loc, old_idx, ctx)
 
        return

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    """ Variability cases to handle. """

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: TransformCtx) -> Any:
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_node(node, self.get_root_node(node), 0, ctx)            
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_to_if(node, ctx)

    @visit.register
    def visit(self, node: ast.IfStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_to_if(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_to_if(node, ctx)

    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_to_if(node, ctx)

    # Preprocessor syntax.

    @visit.register
    def visit(self, node: ast.PreprocInclude, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.SystemLibString, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Function definitions and bodies.

    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ParameterDeclaration, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Arguments.

    @visit.register
    def visit(self, node: ast.ArgumentList, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ParameterList, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.PointerDeclarator, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Expressions.

    @visit.register
    def visit(self, node: ast.ParenthesizedExpression, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.BinaryExpression, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.CallExpression, ctx: TransformCtx) -> Any:    
        self.visit_children(node, ctx)

    # Literals.

    @visit.register
    def visit(self, node: ast.StringLiteral, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)    
    
    @visit.register
    def visit(self, node: ast.NumberLiteral, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Types.

    @visit.register
    def visit(self, node: ast.PrimitiveType, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Misc.

    @visit.register
    def visit(self, node: ast.Comment, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)  
    
    @visit.register
    def visit(self, node: ast.Null, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)  
    
    @visit.register
    def visit(self, node: ast.Declaration, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)   
    
    @visit.register
    def visit(self, node: ast.Identifier, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
