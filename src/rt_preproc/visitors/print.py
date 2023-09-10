from typing import Any
import rt_preproc.parser.ast as ast
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx


class PrintCtx(IVisitorCtx):
    pass


class PrintVisitor(IVisitor):
    """Visitor for printing an AST."""

    @multimethod
    def visit(self, node: ast.AstNode, ctx: PrintCtx) -> Any:
        if len(node.children) > 0:
            for child in node.children:
                child.accept(self, ctx)  # ctx is not used in this visitor
        else:  # leaf node
            print(node.text, end="")
