from typing import Any
import rt_preproc.parser.ast as ast
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from astyle_py import Astyle

class PrintCtx(IVisitorCtx):
    pass


class PrintVisitor(IVisitor):
    """Visitor for printing an AST."""

    def __init__(self, output_file: str = None, use_astyle: bool = False) -> None:
        super().__init__()
        self.output_file = open(output_file, "w") if output_file else None
        self.buffer = ""
        self.use_astyle = use_astyle

    @multimethod
    def visit(self, node: ast.AstNode, ctx: PrintCtx) -> Any:
        if len(node.children) > 0:
            for child in node.children:
                child.accept(self, ctx)  # ctx is not used in this visitor
        else:  # leaf node
            if self.use_astyle:
                self.buffer += node.text
            elif self.output_file is not None:
                self.output_file.write(node.text)
            else:
                print(node.text, end="")
        # if root node, close file and run astyle
        if isinstance(node, ast.TranslationUnit):
            if self.use_astyle:
                formatter = Astyle()
                formatter.set_options('--style=mozilla --mode=c')
                self.buffer = formatter.format(self.buffer)
                if self.output_file is not None:
                    with open(self.output_file, "w") as f:
                        f.write(self.buffer)
                print(self.buffer)
                self.buffer = ""
            if self.output_file is not None:
                self.output_file.close()
