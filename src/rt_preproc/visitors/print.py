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

    def visit_children(
        self, node: ast.AstNode, ctx: PrintCtx, 
        label: str = None,
    ) -> list[Any]:
        if (
            hasattr(node, "children")
            and node.children is not None
            and len(node.children) > 0
        ):
            for i, child in enumerate(node.children):
                child.parent = node
                if hasattr(child, "base_node") and child.base_node is not None:
                    child.text = child.base_node.text
                child.accept(self, PrintCtx(parent=node))
        else: # leaf node
            print(node.get_text(), end="")

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.AstNode, ctx: PrintCtx) -> Any:
        self.visit_children(node, ctx)
