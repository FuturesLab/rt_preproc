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
                child.accept(self, TransformCtx(parent=node))
            return
        return


    def get_root_node(self, node: ast.TreeSitterNode):
        if isinstance(node.parent, ast.TranslationUnit):
            return node.parent
        return self.get_root_node(node.parent)


    def remove_child(self, child: ast.TreeSitterNode, 
                           parent: ast.TreeSitterNode, 
                           ctx: TransformCtx):
        child.parent = None
        parent.children.remove(child)

        if isinstance(parent, ast.PreprocIfdef) and len(parent.children) < 2:
            self.remove_child(parent, parent.parent, ctx)

        return


    def move_node(self, node: ast.TreeSitterNode, 
                        dest: ast.TreeSitterNode, 
                        ctx: TransformCtx):
        self.remove_child(node, node.parent, ctx)
        dest.children.insert(0, node)
        node.parent = dest
        return

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

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
    def visit(self, node: ast.FunctionDefinition, ctx: TransformCtx) -> Any:
        if isinstance(node.parent, ast.PreprocIfdef):
            self.move_node(node, self.get_root_node(node), ctx)            
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ParameterDeclaration, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: TransformCtx) -> Any:
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

    # Statements.

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.IfStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: TransformCtx) -> Any:
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
