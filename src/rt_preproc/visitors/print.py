from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from html import escape


class PrintCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.TreeSitterNode] = None) -> None:
        self.parent = parent


class PrintVisitor(IVisitor):
    """Visitor for performing variability Printations on AST nodes."""

    def __init__(self) -> None:
        self.buf = ""
        self.seen = []

    def visit_children(
        self, node: ast.TreeSitterNode, ctx: PrintCtx, label: str = None
    ) -> list[Any]:

        #print(node, node.parent)

        if len(node.children) == 0:
            raw_text = node.text.decode('utf-8')

            # Avoid "(())" edge case...

            if raw_text != "()": print(raw_text, end='') 
            
        if hasattr(node, "children") and node.children is not None:
            for child in node.children:
                child.parent = node
                if hasattr(child, "base_node"): child.text = child.base_node.text
                child.accept(self, PrintCtx(parent=node))
            return
        return

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    # Preprocessor syntax.

    @visit.register
    def visit(self, node: ast.PreprocInclude, ctx: PrintCtx) -> Any:
        print("#include", end=' ')
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.PreprocIfdef, ctx: PrintCtx) -> Any:
        print('#ifdef', end=' ')
        self.visit_children(node, ctx)
        print("#endif", end='\n')
    
    @visit.register
    def visit(self, node: ast.SystemLibString, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
        print("", end='\n')

    # Function definitions and bodies.

    @visit.register
    def visit(self, node: ast.FunctionDefinition, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.FunctionDeclarator, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ParameterDeclaration, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.CompoundStatement, ctx: PrintCtx) -> Any:
        print("{", end='\n')
        if node.children: self.visit_children(node, ctx)
        print("}", end='\n')

    # Arguments.

    @visit.register
    def visit(self, node: ast.ArgumentList, ctx: PrintCtx) -> Any:
        print("(", end='')
        self.visit_children(node, ctx)
        print(")", end='')
    
    @visit.register
    def visit(self, node: ast.ParameterList, ctx: PrintCtx) -> Any:
        print("(", end='')
        self.visit_children(node, ctx)
        print(")", end='')

    @visit.register
    def visit(self, node: ast.ParameterDeclaration, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.PointerDeclarator, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    # Expressions.

    @visit.register
    def visit(self, node: ast.ParenthesizedExpression, ctx: PrintCtx) -> Any:
        print("(", end="")
        self.visit_children(node, ctx)
        print(")", end="")
    
    @visit.register
    def visit(self, node: ast.BinaryExpression, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.CallExpression, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    # Statements.

    @visit.register
    def visit(self, node: ast.ExpressionStatement, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
        print("", end=";\n")
    
    @visit.register
    def visit(self, node: ast.AssignmentExpression, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast.IfStatement, ctx: PrintCtx) -> Any:
        print("if", end=' ')
        self.visit_children(node, ctx)
    
    @visit.register
    def visit(self, node: ast.ReturnStatement, ctx: PrintCtx) -> Any:
        print("return", end=' ')
        self.visit_children(node, ctx)
        print("", end=';\n')

    @visit.register
    def visit(self, node: ast.InitDeclarator, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)


    # Literals.

    @visit.register
    def visit(self, node: ast.StringLiteral, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)    
    
    @visit.register
    def visit(self, node: ast.NumberLiteral, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    @visit.register
    def visit(self, node: ast._expression, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)

    # Types.

    @visit.register
    def visit(self, node: ast.PrimitiveType, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
        print(" ", end='')

    # Misc.

    @visit.register
    def visit(self, node: ast.Comment, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)  
        print("", end="\n")     

    @visit.register
    def visit(self, node: ast.Null, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)  

    @visit.register
    def visit(self, node: ast.Declaration, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)  
        print(";", end='\n') 

    @visit.register
    def visit(self, node: ast.Identifier, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
        if isinstance(node.parent, ast.PreprocIfdef):
            print("", end='\n')
        else:
            print("", end='')
