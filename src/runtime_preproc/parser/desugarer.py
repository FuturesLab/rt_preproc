from tree_sitter import Parser, Tree
from runtime_preproc.parser import C_LANGUAGE

class Desugarer:
    def __init__(self):
        parser = Parser()
        parser.set_language(C_LANGUAGE)
        self.parser = parser

    def parse(self, bytes) -> Tree:
        return self.parser.parse(bytes)
