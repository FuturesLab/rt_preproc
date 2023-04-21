from abc import ABC, abstractmethod

from rt_preproc.visitors.base import IVisitor


# manually added node base class
# removed ABC for multiple dispatch
class INode(ABC):
    """Node interface"""

    @abstractmethod
    def text(self) -> str:
        pass

    @abstractmethod
    def accept(self, visitor: IVisitor):
        pass
