from typing import Any
import rt_preproc.parser.ast as ast
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx


class PrintCtx(IVisitorCtx):
    pass


class PrintVisitor(IVisitor):
    """Visitor for printing an AST."""

    def __init__(self, output_file: str = None) -> None:
        super().__init__()
        self.output_file = open(output_file, "w") if output_file else None

    @multimethod
    def visit(self, node: ast.AstNode, ctx: PrintCtx) -> Any:
        if len(node.children) > 0:
            for child in node.children:
                child.accept(self, ctx)  # ctx is not used in this visitor
        else:  # leaf node
            if self.output_file is not None:
                self.output_file.write(node.text)
            print(node.text, end="")
