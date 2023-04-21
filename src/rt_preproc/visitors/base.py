from abc import ABC, abstractmethod
from typing import Any


class IVisitorCtx(ABC):
    """Visitor context interface"""

    pass


# manually added visitor base class
class IVisitor(ABC):
    """Visitor interface"""

    @abstractmethod
    def visit(self, node: Any, ctx: IVisitorCtx) -> Any:
        """
        Visits the given node, then recursively visits any children
        """
