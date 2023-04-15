from tree_sitter import Language

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-c',
  ]
)

C_LANGUAGE = Language('build/my-languages.so', 'c')


