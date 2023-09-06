from tree_sitter import Language
from pathlib import Path

here = Path(__file__)
# (here) <- parser <- rt_preproc <- src <- rt_preproc (root)
root = here.parent.parent.parent.parent

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    [
        root / "vendor/tree-sitter-c",
    ],
)

C_LANGUAGE = Language("build/my-languages.so", "c")
