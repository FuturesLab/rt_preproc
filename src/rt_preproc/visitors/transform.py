from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from html import escape
import copy
from rt_preproc.parser.utils import *

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
                if hasattr(child, "base_node"): 
                    child.text = child.base_node.text
                child.accept(self, TransformCtx(parent=node))    
            return
        return

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Below is our two-pass handling of preprocessor blocks.
    # First pass: identify any declarations and handle them first.
    # Second pass: convert preproc blocks to conditional statements.

    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: TransformCtx) -> Any:
        move_declarations(node)
        self.visit_children(node, ctx)
        rewrite_as_if(node)

    # General expressions...

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.IfStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.AssignmentExpression, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Function definitions / declarations...

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: TransformCtx) -> Any:       
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: TransformCtx) -> Any: 
        self.visit_children(node, ctx)

    # Variable definitions / declarations...

    @visit.register
    def visit(self, node: ast.Declaration, ctx: TransformCtx) -> Any:        
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.PreprocInclude, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.SystemLibString, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Arguments.

    @visit.register
    def visit(self, node: ast.ArgumentList, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ParameterList, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.ParameterDeclaration, ctx: TransformCtx) -> Any:
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

    @visit.register
    def visit(self, node: ast.InitDeclarator, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    # Types and literals.

    @visit.register
    def visit(self, node: ast.StringLiteral, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)    
    
    @visit.register
    def visit(self, node: ast.NumberLiteral, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast._expression, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)    

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
    def visit(self, node: ast.Identifier, ctx: TransformCtx) -> Any:
        self.visit_children(node, ctx)
