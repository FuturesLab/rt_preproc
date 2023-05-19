
""" Function definition. """

("""(preproc_ifdef(
  (identifier) @macro
  (function_definition) @funcDef
))""") # Global


""" Function declaration. """

("""(preproc_ifdef(
  (identifier) @macro
  (declaration
    (function_declarator) @funcDecl
)))""") # Global


""" Variable declaration. """

("""(preproc_ifdef (
  (identifier) @macro 
  (declaration
    () @varDecl
))""") # Global

("""(compound_statement
(preproc_ifdef (
  (identifier) @macro 
  (declaration) @varDecl
))))""") # Local


""" Variable initialization. """

("""(preproc_ifdef (
  (identifier) @macro 
  (expression_statement
    (assignment_expression) @varInit
)))""") # Global

("""(compound_statement
(preproc_ifdef (
  (identifier) @macro 
  (expression_statement
    (assignment_expression) @varInit
))))""") # Local


""" Function calls: """

("""(preproc_ifdef (
  (expression_statement
    (call_expression) @funcCall
)))""") # Global

("""(compound_statement
(preproc_ifdef (
  (expression_statement
    (call_expression) @funcCall
))))""") # Local
