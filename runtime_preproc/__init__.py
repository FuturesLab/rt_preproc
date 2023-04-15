from tree_sitter import Language, Parser

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-c',
  ]
)

C_LANGUAGE = Language('build/my-languages.so', 'c')

parser = Parser()
parser.set_language(C_LANGUAGE)

tree = parser.parse(bytes("""
#ifdef b
	int x = 0;
#else
	float x = 0;
#endif
""", "utf8"))


print("---- C FILE ----")
print(tree.text.decode('utf8'))
print("---- AST -------")
print(tree.root_node.sexp())
