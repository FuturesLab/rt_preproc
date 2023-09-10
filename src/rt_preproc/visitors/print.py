from typing import Any
import rt_preproc.parser.ast as ast
from typing import Optional
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
import logging

logger = logging.getLogger(__name__)


class PrintCtx(IVisitorCtx):
    def __init__(self, parent: Optional[ast.AstNode] = None) -> None:
        self.parent = parent


class PrintVisitor(IVisitor):
    """Visitor for performing variability Printations on AST nodes."""

    def __init__(self) -> None:
        self.buf = ""
        self.seen = []

    @multimethod
    def visit(self, node: ast.AstNode, ctx: PrintCtx) -> Any:
        if node.children is not None and len(node.children) > 0:
            for child in node.children:
                child.accept(self, PrintCtx(parent=node))
        else:  # leaf node
            print(node.text, end="")
