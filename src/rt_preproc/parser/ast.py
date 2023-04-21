from typing import Union, Any, Optional, List

from tree_sitter_types.parser import load_language, install_parser, parse_node


class TreeSitterNode:
    base_node: Any

    def text(self):
        return self.base_node.text


class _abstractDeclarator(TreeSitterNode):
    field_names = []
    children: None


class _declarator(TreeSitterNode):
    field_names = []
    children: None


class _expression(TreeSitterNode):
    field_names = []
    children: None


class _fieldDeclarator(TreeSitterNode):
    field_names = []
    children: None


class _statement(TreeSitterNode):
    field_names = []
    children: None


class _typeDeclarator(TreeSitterNode):
    field_names = []
    children: None


class _typeSpecifier(TreeSitterNode):
    field_names = []
    children: None


class AbstractArrayDeclarator(TreeSitterNode):
    field_names = ["declarator", "size"]
    declarator: Optional["_abstractDeclarator"]
    size: Optional[Union["str", "_expression"]]
    children: Optional[List["TypeQualifier"]]


class AbstractFunctionDeclarator(TreeSitterNode):
    field_names = ["declarator", "parameters"]
    declarator: Optional["_abstractDeclarator"]
    parameters: "ParameterList"
    children: None


class AbstractParenthesizedDeclarator(TreeSitterNode):
    field_names = []
    children: "_abstractDeclarator"


class AbstractPointerDeclarator(TreeSitterNode):
    field_names = ["declarator"]
    declarator: Optional["_abstractDeclarator"]
    children: Optional[List["TypeQualifier"]]


class ArgumentList(TreeSitterNode):
    field_names = []
    children: Optional[List[Union["_expression", "PreprocDefined"]]]


class ArrayDeclarator(TreeSitterNode):
    field_names = ["declarator", "size"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    size: Optional[Union["str", "_expression"]]
    children: Optional[List["TypeQualifier"]]


class AssignmentExpression(TreeSitterNode):
    field_names = ["left", "operator", "right"]
    left: Union[
        "CallExpression",
        "FieldExpression",
        "Identifier",
        "ParenthesizedExpression",
        "PointerExpression",
        "SubscriptExpression",
    ]
    operator: Union[
        "str", "str", "str", "str", "str", "str", "str", "str", "str", "str", "str"
    ]
    right: "_expression"
    children: None


class Attribute(TreeSitterNode):
    field_names = ["name", "prefix"]
    name: "Identifier"
    prefix: Optional["Identifier"]
    children: Optional["ArgumentList"]


class AttributeDeclaration(TreeSitterNode):
    field_names = []
    children: List["Attribute"]


class AttributeSpecifier(TreeSitterNode):
    field_names = []
    children: "ArgumentList"


class AttributedDeclarator(TreeSitterNode):
    field_names = []
    children: List[
        Union[
            "_declarator", "_fieldDeclarator", "_typeDeclarator", "AttributeDeclaration"
        ]
    ]


class AttributedStatement(TreeSitterNode):
    field_names = []
    children: List[Union["_statement", "AttributeDeclaration"]]


class BinaryExpression(TreeSitterNode):
    field_names = ["left", "operator", "right"]
    left: Union["_expression", "PreprocDefined"]
    operator: Union[
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
        "str",
    ]
    right: Union["_expression", "PreprocDefined"]
    children: None


class BitfieldClause(TreeSitterNode):
    field_names = []
    children: "_expression"


class BreakStatement(TreeSitterNode):
    field_names = []
    children: None


class CallExpression(TreeSitterNode):
    field_names = ["arguments", "function"]
    arguments: "ArgumentList"
    function: "_expression"
    children: None


class CaseStatement(TreeSitterNode):
    field_names = ["value"]
    value: Optional["_expression"]
    children: Optional[
        List[
            Union[
                "AttributedStatement",
                "BreakStatement",
                "CompoundStatement",
                "ContinueStatement",
                "Declaration",
                "DoStatement",
                "ExpressionStatement",
                "ForStatement",
                "GotoStatement",
                "IfStatement",
                "LabeledStatement",
                "ReturnStatement",
                "SwitchStatement",
                "TypeDefinition",
                "WhileStatement",
            ]
        ]
    ]


class CastExpression(TreeSitterNode):
    field_names = ["type", "value"]
    type: "TypeDescriptor"
    value: "_expression"
    children: None


class CharLiteral(TreeSitterNode):
    field_names = []
    children: Optional["EscapeSequence"]


class CommaExpression(TreeSitterNode):
    field_names = ["left", "right"]
    left: "_expression"
    right: Union["_expression", "CommaExpression"]
    children: None


class CompoundLiteralExpression(TreeSitterNode):
    field_names = ["type", "value"]
    type: "TypeDescriptor"
    value: "InitializerList"
    children: None


class CompoundStatement(TreeSitterNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class ConcatenatedString(TreeSitterNode):
    field_names = []
    children: List["StringLiteral"]


class ConditionalExpression(TreeSitterNode):
    field_names = ["alternative", "condition", "consequence"]
    alternative: "_expression"
    condition: "_expression"
    consequence: "_expression"
    children: None


class ContinueStatement(TreeSitterNode):
    field_names = []
    children: None


class Declaration(TreeSitterNode):
    field_names = ["declarator", "type"]
    declarator: List[Union["_declarator", "InitDeclarator"]]
    type: "_typeSpecifier"
    children: Optional[
        List[
            Union[
                "AttributeDeclaration",
                "AttributeSpecifier",
                "MsDeclspecModifier",
                "StorageClassSpecifier",
                "TypeQualifier",
            ]
        ]
    ]


class DeclarationList(TreeSitterNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class DoStatement(TreeSitterNode):
    field_names = ["body", "condition"]
    body: "_statement"
    condition: "ParenthesizedExpression"
    children: None


class EnumSpecifier(TreeSitterNode):
    field_names = ["body", "name"]
    body: Optional["EnumeratorList"]
    name: Optional["TypeIdentifier"]
    children: None


class Enumerator(TreeSitterNode):
    field_names = ["name", "value"]
    name: "Identifier"
    value: Optional["_expression"]
    children: None


class EnumeratorList(TreeSitterNode):
    field_names = []
    children: Optional[List["Enumerator"]]


class ExpressionStatement(TreeSitterNode):
    field_names = []
    children: Optional[Union["_expression", "CommaExpression"]]


class FieldDeclaration(TreeSitterNode):
    field_names = ["declarator", "type"]
    declarator: Optional[List["_fieldDeclarator"]]
    type: "_typeSpecifier"
    children: Optional[
        List[
            Union[
                "AttributeDeclaration",
                "AttributeSpecifier",
                "BitfieldClause",
                "MsDeclspecModifier",
                "StorageClassSpecifier",
                "TypeQualifier",
            ]
        ]
    ]


class FieldDeclarationList(TreeSitterNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "FieldDeclaration",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
            ]
        ]
    ]


class FieldDesignator(TreeSitterNode):
    field_names = []
    children: "FieldIdentifier"


class FieldExpression(TreeSitterNode):
    field_names = ["argument", "field", "operator"]
    argument: "_expression"
    field: "FieldIdentifier"
    operator: Union["str", "str"]
    children: None


class ForStatement(TreeSitterNode):
    field_names = ["body", "condition", "initializer", "update"]
    body: "_statement"
    condition: Optional[Union["_expression", "CommaExpression"]]
    initializer: Optional[Union["_expression", "CommaExpression", "Declaration"]]
    update: Optional[Union["_expression", "CommaExpression"]]
    children: None


class FunctionDeclarator(TreeSitterNode):
    field_names = ["declarator", "parameters"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    parameters: "ParameterList"
    children: Optional[List["AttributeSpecifier"]]


class FunctionDefinition(TreeSitterNode):
    field_names = ["body", "declarator", "type"]
    body: "CompoundStatement"
    declarator: "_declarator"
    type: "_typeSpecifier"
    children: Optional[
        List[
            Union[
                "AttributeDeclaration",
                "AttributeSpecifier",
                "MsCallModifier",
                "MsDeclspecModifier",
                "StorageClassSpecifier",
                "TypeQualifier",
            ]
        ]
    ]


class GotoStatement(TreeSitterNode):
    field_names = ["label"]
    label: "StatementIdentifier"
    children: None


class IfStatement(TreeSitterNode):
    field_names = ["alternative", "condition", "consequence"]
    alternative: Optional["_statement"]
    condition: "ParenthesizedExpression"
    consequence: "_statement"
    children: None


class InitDeclarator(TreeSitterNode):
    field_names = ["declarator", "value"]
    declarator: "_declarator"
    value: Union["_expression", "InitializerList"]
    children: None


class InitializerList(TreeSitterNode):
    field_names = []
    children: Optional[List[Union["_expression", "InitializerList", "InitializerPair"]]]


class InitializerPair(TreeSitterNode):
    field_names = ["designator", "value"]
    designator: List[Union["FieldDesignator", "SubscriptDesignator"]]
    value: Union["_expression", "InitializerList"]
    children: None


class LabeledStatement(TreeSitterNode):
    field_names = ["label"]
    label: "StatementIdentifier"
    children: "_statement"


class LinkageSpecification(TreeSitterNode):
    field_names = ["body", "value"]
    body: Union["Declaration", "DeclarationList", "FunctionDefinition"]
    value: "StringLiteral"
    children: None


class MacroTypeSpecifier(TreeSitterNode):
    field_names = ["name", "type"]
    name: "Identifier"
    type: "TypeDescriptor"
    children: None


class MsBasedModifier(TreeSitterNode):
    field_names = []
    children: "ArgumentList"


class MsCallModifier(TreeSitterNode):
    field_names = []
    children: None


class MsDeclspecModifier(TreeSitterNode):
    field_names = []
    children: "Identifier"


class MsPointerModifier(TreeSitterNode):
    field_names = []
    children: Union[
        "MsRestrictModifier",
        "MsSignedPtrModifier",
        "MsUnalignedPtrModifier",
        "MsUnsignedPtrModifier",
    ]


class MsUnalignedPtrModifier(TreeSitterNode):
    field_names = []
    children: None


class ParameterDeclaration(TreeSitterNode):
    field_names = ["declarator", "type"]
    declarator: Optional[Union["_abstractDeclarator", "_declarator"]]
    type: "_typeSpecifier"
    children: Optional[
        List[
            Union[
                "AttributeDeclaration",
                "AttributeSpecifier",
                "MsDeclspecModifier",
                "StorageClassSpecifier",
                "TypeQualifier",
            ]
        ]
    ]


class ParameterList(TreeSitterNode):
    field_names = []
    children: Optional[List[Union["ParameterDeclaration", "VariadicParameter"]]]


class ParenthesizedDeclarator(TreeSitterNode):
    field_names = []
    children: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]


class ParenthesizedExpression(TreeSitterNode):
    field_names = []
    children: Union["_expression", "CommaExpression", "PreprocDefined"]


class PointerDeclarator(TreeSitterNode):
    field_names = ["declarator"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    children: Optional[
        List[Union["MsBasedModifier", "MsPointerModifier", "TypeQualifier"]]
    ]


class PointerExpression(TreeSitterNode):
    field_names = ["argument", "operator"]
    argument: "_expression"
    operator: Union["str", "str"]
    children: None


class PreprocCall(TreeSitterNode):
    field_names = ["argument", "directive"]
    argument: Optional["PreprocArg"]
    directive: "PreprocDirective"
    children: None


class PreprocDef(TreeSitterNode):
    field_names = ["name", "value"]
    name: "Identifier"
    value: Optional["PreprocArg"]
    children: None


class PreprocDefined(TreeSitterNode):
    field_names = []
    children: "Identifier"


class PreprocElif(TreeSitterNode):
    field_names = ["alternative", "condition"]
    alternative: Optional[Union["PreprocElif", "PreprocElse"]]
    condition: Union[
        "BinaryExpression",
        "CallExpression",
        "CharLiteral",
        "Identifier",
        "NumberLiteral",
        "ParenthesizedExpression",
        "PreprocDefined",
        "UnaryExpression",
    ]
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FieldDeclaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class PreprocElse(TreeSitterNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FieldDeclaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class PreprocFunctionDef(TreeSitterNode):
    field_names = ["name", "parameters", "value"]
    name: "Identifier"
    parameters: "PreprocParams"
    value: Optional["PreprocArg"]
    children: None


class PreprocIf(TreeSitterNode):
    field_names = ["alternative", "condition"]
    alternative: Optional[Union["PreprocElif", "PreprocElse"]]
    condition: Union[
        "BinaryExpression",
        "CallExpression",
        "CharLiteral",
        "Identifier",
        "NumberLiteral",
        "ParenthesizedExpression",
        "PreprocDefined",
        "UnaryExpression",
    ]
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FieldDeclaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class PreprocIfdef(TreeSitterNode):
    field_names = ["alternative", "name"]
    alternative: Optional[Union["PreprocElif", "PreprocElse"]]
    name: "Identifier"
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FieldDeclaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class PreprocInclude(TreeSitterNode):
    field_names = ["path"]
    path: Union["CallExpression", "Identifier", "StringLiteral", "SystemLibString"]
    children: None


class PreprocParams(TreeSitterNode):
    field_names = []
    children: Optional[List["Identifier"]]


class ReturnStatement(TreeSitterNode):
    field_names = []
    children: Optional[Union["_expression", "CommaExpression"]]


class SizedTypeSpecifier(TreeSitterNode):
    field_names = ["type"]
    type: Optional[Union["PrimitiveType", "TypeIdentifier"]]
    children: None


class SizeofExpression(TreeSitterNode):
    field_names = ["type", "value"]
    type: Optional["TypeDescriptor"]
    value: Optional["_expression"]
    children: None


class StorageClassSpecifier(TreeSitterNode):
    field_names = []
    children: None


class StringLiteral(TreeSitterNode):
    field_names = []
    children: Optional[List["EscapeSequence"]]


class StructSpecifier(TreeSitterNode):
    field_names = ["body", "name"]
    body: Optional["FieldDeclarationList"]
    name: Optional["TypeIdentifier"]
    children: Optional["MsDeclspecModifier"]


class SubscriptDesignator(TreeSitterNode):
    field_names = []
    children: "_expression"


class SubscriptExpression(TreeSitterNode):
    field_names = ["argument", "index"]
    argument: "_expression"
    index: "_expression"
    children: None


class SwitchStatement(TreeSitterNode):
    field_names = ["body", "condition"]
    body: "CompoundStatement"
    condition: "ParenthesizedExpression"
    children: None


class TranslationUnit(TreeSitterNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "_statement",
                "_typeSpecifier",
                "Declaration",
                "FunctionDefinition",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "TypeDefinition",
            ]
        ]
    ]


class TypeDefinition(TreeSitterNode):
    field_names = ["declarator", "type"]
    declarator: List["_typeDeclarator"]
    type: "_typeSpecifier"
    children: Optional[List["TypeQualifier"]]


class TypeDescriptor(TreeSitterNode):
    field_names = ["declarator", "type"]
    declarator: Optional["_abstractDeclarator"]
    type: "_typeSpecifier"
    children: Optional[List["TypeQualifier"]]


class TypeQualifier(TreeSitterNode):
    field_names = []
    children: None


class UnaryExpression(TreeSitterNode):
    field_names = ["argument", "operator"]
    argument: Union["_expression", "PreprocDefined"]
    operator: Union["str", "str", "str", "str"]
    children: None


class UnionSpecifier(TreeSitterNode):
    field_names = ["body", "name"]
    body: Optional["FieldDeclarationList"]
    name: Optional["TypeIdentifier"]
    children: Optional["MsDeclspecModifier"]


class UpdateExpression(TreeSitterNode):
    field_names = ["argument", "operator"]
    argument: "_expression"
    operator: Union["str", "str"]
    children: None


class VariadicParameter(TreeSitterNode):
    field_names = []
    children: None


class WhileStatement(TreeSitterNode):
    field_names = ["body", "condition"]
    body: "_statement"
    condition: "ParenthesizedExpression"
    children: None


class Comment(TreeSitterNode):
    field_names = []
    children: None


class EscapeSequence(TreeSitterNode):
    field_names = []
    children: None


class FalseBool(TreeSitterNode):
    field_names = []
    children: None


class FieldIdentifier(TreeSitterNode):
    field_names = []
    children: None


class Identifier(TreeSitterNode):
    field_names = []
    children: None


class MsRestrictModifier(TreeSitterNode):
    field_names = []
    children: None


class MsSignedPtrModifier(TreeSitterNode):
    field_names = []
    children: None


class MsUnsignedPtrModifier(TreeSitterNode):
    field_names = []
    children: None


class Null(TreeSitterNode):
    field_names = []
    children: None


class NumberLiteral(TreeSitterNode):
    field_names = []
    children: None


class PreprocArg(TreeSitterNode):
    field_names = []
    children: None


class PreprocDirective(TreeSitterNode):
    field_names = []
    children: None


class PrimitiveType(TreeSitterNode):
    field_names = []
    children: None


class StatementIdentifier(TreeSitterNode):
    field_names = []
    children: None


class SystemLibString(TreeSitterNode):
    field_names = []
    children: None


class TrueBool(TreeSitterNode):
    field_names = []
    children: None


class TypeIdentifier(TreeSitterNode):
    field_names = []
    children: None


type_name_to_class = {
    "_abstract_declarator": _abstractDeclarator,
    "_declarator": _declarator,
    "_expression": _expression,
    "_field_declarator": _fieldDeclarator,
    "_statement": _statement,
    "_type_declarator": _typeDeclarator,
    "_type_specifier": _typeSpecifier,
    "abstract_array_declarator": AbstractArrayDeclarator,
    "abstract_function_declarator": AbstractFunctionDeclarator,
    "abstract_parenthesized_declarator": AbstractParenthesizedDeclarator,
    "abstract_pointer_declarator": AbstractPointerDeclarator,
    "argument_list": ArgumentList,
    "array_declarator": ArrayDeclarator,
    "assignment_expression": AssignmentExpression,
    "attribute": Attribute,
    "attribute_declaration": AttributeDeclaration,
    "attribute_specifier": AttributeSpecifier,
    "attributed_declarator": AttributedDeclarator,
    "attributed_statement": AttributedStatement,
    "binary_expression": BinaryExpression,
    "bitfield_clause": BitfieldClause,
    "break_statement": BreakStatement,
    "call_expression": CallExpression,
    "case_statement": CaseStatement,
    "cast_expression": CastExpression,
    "char_literal": CharLiteral,
    "comma_expression": CommaExpression,
    "compound_literal_expression": CompoundLiteralExpression,
    "compound_statement": CompoundStatement,
    "concatenated_string": ConcatenatedString,
    "conditional_expression": ConditionalExpression,
    "continue_statement": ContinueStatement,
    "declaration": Declaration,
    "declaration_list": DeclarationList,
    "do_statement": DoStatement,
    "enum_specifier": EnumSpecifier,
    "enumerator": Enumerator,
    "enumerator_list": EnumeratorList,
    "expression_statement": ExpressionStatement,
    "field_declaration": FieldDeclaration,
    "field_declaration_list": FieldDeclarationList,
    "field_designator": FieldDesignator,
    "field_expression": FieldExpression,
    "for_statement": ForStatement,
    "function_declarator": FunctionDeclarator,
    "function_definition": FunctionDefinition,
    "goto_statement": GotoStatement,
    "if_statement": IfStatement,
    "init_declarator": InitDeclarator,
    "initializer_list": InitializerList,
    "initializer_pair": InitializerPair,
    "labeled_statement": LabeledStatement,
    "linkage_specification": LinkageSpecification,
    "macro_type_specifier": MacroTypeSpecifier,
    "ms_based_modifier": MsBasedModifier,
    "ms_call_modifier": MsCallModifier,
    "ms_declspec_modifier": MsDeclspecModifier,
    "ms_pointer_modifier": MsPointerModifier,
    "ms_unaligned_ptr_modifier": MsUnalignedPtrModifier,
    "parameter_declaration": ParameterDeclaration,
    "parameter_list": ParameterList,
    "parenthesized_declarator": ParenthesizedDeclarator,
    "parenthesized_expression": ParenthesizedExpression,
    "pointer_declarator": PointerDeclarator,
    "pointer_expression": PointerExpression,
    "preproc_call": PreprocCall,
    "preproc_def": PreprocDef,
    "preproc_defined": PreprocDefined,
    "preproc_elif": PreprocElif,
    "preproc_else": PreprocElse,
    "preproc_function_def": PreprocFunctionDef,
    "preproc_if": PreprocIf,
    "preproc_ifdef": PreprocIfdef,
    "preproc_include": PreprocInclude,
    "preproc_params": PreprocParams,
    "return_statement": ReturnStatement,
    "sized_type_specifier": SizedTypeSpecifier,
    "sizeof_expression": SizeofExpression,
    "storage_class_specifier": StorageClassSpecifier,
    "string_literal": StringLiteral,
    "struct_specifier": StructSpecifier,
    "subscript_designator": SubscriptDesignator,
    "subscript_expression": SubscriptExpression,
    "switch_statement": SwitchStatement,
    "translation_unit": TranslationUnit,
    "type_definition": TypeDefinition,
    "type_descriptor": TypeDescriptor,
    "type_qualifier": TypeQualifier,
    "unary_expression": UnaryExpression,
    "union_specifier": UnionSpecifier,
    "update_expression": UpdateExpression,
    "variadic_parameter": VariadicParameter,
    "while_statement": WhileStatement,
    "comment": Comment,
    "escape_sequence": EscapeSequence,
    "false": False,
    "field_identifier": FieldIdentifier,
    "identifier": Identifier,
    "ms_restrict_modifier": MsRestrictModifier,
    "ms_signed_ptr_modifier": MsSignedPtrModifier,
    "ms_unsigned_ptr_modifier": MsUnsignedPtrModifier,
    "null": Null,
    "number_literal": NumberLiteral,
    "preproc_arg": PreprocArg,
    "preproc_directive": PreprocDirective,
    "primitive_type": PrimitiveType,
    "statement_identifier": StatementIdentifier,
    "system_lib_string": SystemLibString,
    "true": True,
    "type_identifier": TypeIdentifier,
}
