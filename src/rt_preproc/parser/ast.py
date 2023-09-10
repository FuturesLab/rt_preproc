from typing import Union, Any, Optional, List, Self
from tree_sitter import Node as BaseTsNode
from rt_preproc.parser.base import INode
from rt_preproc.visitors.base import IVisitor, IVisitorCtx


class AstNode(INode):
    base_node: BaseTsNode
    parent: Optional[Self]
    field_names: List[str]
    children: Optional[List[Self]]
    children_named_idxs: List[Optional[int]]
    named_children: Optional[List[Self]]
    text: Optional[str]
    """
    This is only defined on leaf nodes.
    """

    def get_text(self) -> str:
        return self.base_node.text.decode("utf8")

    # this is a manual change to the generated code
    def accept(self, visitor: IVisitor, ctx: IVisitorCtx):
        return visitor.visit(self, ctx)

    @staticmethod
    def reify(base_node: BaseTsNode, include_whitespace: bool = True) -> "AstNode":
        ast_node = (
            type_name_to_class[base_node.type]()
            if base_node.type in type_name_to_class
            else Unnamed()
        )
        ast_node.base_node = base_node
        ast_node.parent = None
        ast_node.children = []
        ast_node.children_named_idxs = []
        for i, child in enumerate(base_node.children):
            if include_whitespace and i > 0:
                # if the previous child ends before the current child starts
                if base_node.children[i - 1].end_point[0] < child.start_point[0]:
                    ast_node.children.append(
                        Whitespace(
                            "\n"
                            * (
                                child.start_point[0]
                                - base_node.children[i - 1].end_point[0]
                            )
                        )
                    )
                    if child.start_point[1] > 0:
                        ast_node.children.append(
                            Whitespace(" " * (child.start_point[1]))
                        )
                elif base_node.children[i - 1].end_point[1] < child.start_point[1]:
                    ast_node.children.append(
                        Whitespace(
                            " "
                            * (
                                child.start_point[1]
                                - base_node.children[i - 1].end_point[1]
                            )
                        )
                    )
            ast_node.children.append(AstNode.reify(child, include_whitespace))
        # if the last child ends before the base node ends
        if include_whitespace and len(base_node.children) > 0:
            if base_node.children[-1].end_point[0] < base_node.end_point[0]:
                ast_node.children.append(
                    Whitespace(
                        "\n"
                        * (base_node.end_point[0] - base_node.children[-1].end_point[0])
                    )
                )
                if base_node.start_point[1] > 0:
                    ast_node.children.append(
                        Whitespace(" " * (child.start_point[1]))
                    )
            elif base_node.children[-1].end_point[1] < base_node.end_point[1]:
                ast_node.children.append(
                    Whitespace(
                        " "
                        * (base_node.end_point[1] - base_node.children[-1].end_point[1])
                    )
                )
        for child in ast_node.children:
            ast_node.children_named_idxs.append(
                next(
                    (
                        idx
                        for idx, node in enumerate(base_node.named_children)
                        if hasattr(child, "base_node")
                        and child.base_node is not None
                        and node.id == child.base_node.id
                    ),
                    None,
                )
            )
        assert (
            sum(1 for val in ast_node.children_named_idxs if val is not None)
            == base_node.named_child_count
        )
        ast_node.named_children = [AstNode.reify(x) for x in base_node.named_children]
        if len(ast_node.children) == 0:
            ast_node.text = base_node.text.decode("utf8")
        else:
            ast_node.text = None
        return ast_node


class _abstractDeclarator(AstNode):
    field_names = []
    children: None


class _declarator(AstNode):
    field_names = []
    children: None


class _expression(AstNode):
    field_names = []
    children: None


class _fieldDeclarator(AstNode):
    field_names = []
    children: None


class _statement(AstNode):
    field_names = []
    children: None


class _typeDeclarator(AstNode):
    field_names = []
    children: None


class _typeSpecifier(AstNode):
    field_names = []
    children: None


class AbstractArrayDeclarator(AstNode):
    field_names = ["declarator", "size"]
    declarator: Optional["_abstractDeclarator"]
    size: Optional[Union["str", "_expression"]]
    children: Optional[List["TypeQualifier"]]


class AbstractFunctionDeclarator(AstNode):
    field_names = ["declarator", "parameters"]
    declarator: Optional["_abstractDeclarator"]
    parameters: "ParameterList"
    children: None


class AbstractParenthesizedDeclarator(AstNode):
    field_names = []
    children: "_abstractDeclarator"


class AbstractPointerDeclarator(AstNode):
    field_names = ["declarator"]
    declarator: Optional["_abstractDeclarator"]
    children: Optional[List["TypeQualifier"]]


class AlignofExpression(AstNode):
    field_names = ["type"]
    type: "TypeDescriptor"
    children: None


class ArgumentList(AstNode):
    field_names = []
    children: Optional[
        List[Union["_expression", "CompoundStatement", "PreprocDefined"]]
    ]


class ArrayDeclarator(AstNode):
    field_names = ["declarator", "size"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    size: Optional[Union["str", "_expression"]]
    children: Optional[List["TypeQualifier"]]


class AssignmentExpression(AstNode):
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


class Attribute(AstNode):
    field_names = ["name", "prefix"]
    name: "Identifier"
    prefix: Optional["Identifier"]
    children: Optional["ArgumentList"]


class AttributeDeclaration(AstNode):
    field_names = []
    children: List["Attribute"]


class AttributeSpecifier(AstNode):
    field_names = []
    children: "ArgumentList"


class AttributedDeclarator(AstNode):
    field_names = []
    children: List[
        Union[
            "_declarator", "_fieldDeclarator", "_typeDeclarator", "AttributeDeclaration"
        ]
    ]


class AttributedStatement(AstNode):
    field_names = []
    children: List[Union["_statement", "AttributeDeclaration"]]


class BinaryExpression(AstNode):
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


class BitfieldClause(AstNode):
    field_names = []
    children: "_expression"


class BreakStatement(AstNode):
    field_names = []
    children: None


class CallExpression(AstNode):
    field_names = ["arguments", "function"]
    arguments: "ArgumentList"
    function: "_expression"
    children: None


class CaseStatement(AstNode):
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


class CastExpression(AstNode):
    field_names = ["type", "value"]
    type: "TypeDescriptor"
    value: "_expression"
    children: None


class CharLiteral(AstNode):
    field_names = []
    children: Union["Character", "EscapeSequence"]


class CommaExpression(AstNode):
    field_names = ["left", "right"]
    left: "_expression"
    right: Union["_expression", "CommaExpression"]
    children: None


class CompoundLiteralExpression(AstNode):
    field_names = ["type", "value"]
    type: "TypeDescriptor"
    value: "InitializerList"
    children: None


class CompoundStatement(AstNode):
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


class ConcatenatedString(AstNode):
    field_names = []
    children: List[Union["Identifier", "StringLiteral"]]


class ConditionalExpression(AstNode):
    field_names = ["alternative", "condition", "consequence"]
    alternative: "_expression"
    condition: "_expression"
    consequence: Optional["_expression"]
    children: None


class ContinueStatement(AstNode):
    field_names = []
    children: None


class Declaration(AstNode):
    field_names = ["declarator", "type"]
    declarator: List[Union["_declarator", "GnuAsmExpression", "InitDeclarator"]]
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


class DeclarationList(AstNode):
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


class DoStatement(AstNode):
    field_names = ["body", "condition"]
    body: "_statement"
    condition: "ParenthesizedExpression"
    children: None


class ElseClause(AstNode):
    field_names = []
    children: "_statement"


class EnumSpecifier(AstNode):
    field_names = ["body", "name", "underlying_type"]
    body: Optional["EnumeratorList"]
    name: Optional["TypeIdentifier"]
    underlying_type: Optional["PrimitiveType"]
    children: Optional["AttributeSpecifier"]


class Enumerator(AstNode):
    field_names = ["name", "value"]
    name: "Identifier"
    value: Optional["_expression"]
    children: None


class EnumeratorList(AstNode):
    field_names = []
    children: Optional[List["Enumerator"]]


class ExpressionStatement(AstNode):
    field_names = []
    children: Optional[Union["_expression", "CommaExpression"]]


class FieldDeclaration(AstNode):
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


class FieldDeclarationList(AstNode):
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


class FieldDesignator(AstNode):
    field_names = []
    children: "FieldIdentifier"


class FieldExpression(AstNode):
    field_names = ["argument", "field", "operator"]
    argument: "_expression"
    field: "FieldIdentifier"
    operator: Union["str", "str"]
    children: None


class ForStatement(AstNode):
    field_names = ["body", "condition", "initializer", "update"]
    body: "_statement"
    condition: Optional[Union["_expression", "CommaExpression"]]
    initializer: Optional[Union["_expression", "CommaExpression", "Declaration"]]
    update: Optional[Union["_expression", "CommaExpression"]]
    children: None


class FunctionDeclarator(AstNode):
    field_names = ["declarator", "parameters"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    parameters: "ParameterList"
    children: Optional[List[Union["AttributeSpecifier", "GnuAsmExpression"]]]


class FunctionDefinition(AstNode):
    field_names = ["body", "declarator", "type"]
    body: "CompoundStatement"
    declarator: "_declarator"
    type: "_typeSpecifier"
    children: Optional[
        List[
            Union[
                "AttributeDeclaration",
                "AttributeSpecifier",
                "Declaration",
                "MsCallModifier",
                "MsDeclspecModifier",
                "StorageClassSpecifier",
                "TypeQualifier",
            ]
        ]
    ]


class GenericExpression(AstNode):
    field_names = []
    children: List[Union["_expression", "TypeDescriptor"]]


class GnuAsmClobberList(AstNode):
    field_names = ["register"]
    register: Optional[List["StringLiteral"]]
    children: None


class GnuAsmExpression(AstNode):
    field_names = [
        "assembly_code",
        "clobbers",
        "goto_labels",
        "input_operands",
        "output_operands",
    ]
    assembly_code: Union["ConcatenatedString", "StringLiteral"]
    clobbers: Optional["GnuAsmClobberList"]
    goto_labels: Optional["GnuAsmGotoList"]
    input_operands: Optional["GnuAsmInputOperandList"]
    output_operands: Optional["GnuAsmOutputOperandList"]
    children: Optional[List["GnuAsmQualifier"]]


class GnuAsmGotoList(AstNode):
    field_names = ["label"]
    label: Optional[List["Identifier"]]
    children: None


class GnuAsmInputOperand(AstNode):
    field_names = ["constraint", "symbol", "value"]
    constraint: "StringLiteral"
    symbol: Optional["Identifier"]
    value: "_expression"
    children: None


class GnuAsmInputOperandList(AstNode):
    field_names = ["operand"]
    operand: Optional[List["GnuAsmInputOperand"]]
    children: None


class GnuAsmOutputOperand(AstNode):
    field_names = ["constraint", "symbol", "value"]
    constraint: "StringLiteral"
    symbol: Optional["Identifier"]
    value: "Identifier"
    children: None


class GnuAsmOutputOperandList(AstNode):
    field_names = ["operand"]
    operand: Optional[List["GnuAsmOutputOperand"]]
    children: None


class GnuAsmQualifier(AstNode):
    field_names = []
    children: None


class GotoStatement(AstNode):
    field_names = ["label"]
    label: "StatementIdentifier"
    children: None


class IfStatement(AstNode):
    field_names = ["alternative", "condition", "consequence"]
    alternative: Optional["ElseClause"]
    condition: "ParenthesizedExpression"
    consequence: "_statement"
    children: None


class InitDeclarator(AstNode):
    field_names = ["declarator", "value"]
    declarator: "_declarator"
    value: Union["_expression", "InitializerList"]
    children: None


class InitializerList(AstNode):
    field_names = []
    children: Optional[List[Union["_expression", "InitializerList", "InitializerPair"]]]


class InitializerPair(AstNode):
    field_names = ["designator", "value"]
    designator: List[Union["FieldDesignator", "SubscriptDesignator"]]
    value: Union["_expression", "InitializerList"]
    children: None


class LabeledStatement(AstNode):
    field_names = ["label"]
    label: "StatementIdentifier"
    children: "_statement"


class LinkageSpecification(AstNode):
    field_names = ["body", "value"]
    body: Union["Declaration", "DeclarationList", "FunctionDefinition"]
    value: "StringLiteral"
    children: None


class MacroTypeSpecifier(AstNode):
    field_names = ["name", "type"]
    name: "Identifier"
    type: "TypeDescriptor"
    children: None


class MsBasedModifier(AstNode):
    field_names = []
    children: "ArgumentList"


class MsCallModifier(AstNode):
    field_names = []
    children: None


class MsDeclspecModifier(AstNode):
    field_names = []
    children: "Identifier"


class MsPointerModifier(AstNode):
    field_names = []
    children: Union[
        "MsRestrictModifier",
        "MsSignedPtrModifier",
        "MsUnalignedPtrModifier",
        "MsUnsignedPtrModifier",
    ]


class MsUnalignedPtrModifier(AstNode):
    field_names = []
    children: None


class Null(AstNode):
    field_names = []
    children: None


class OffsetofExpression(AstNode):
    field_names = ["member", "type"]
    member: "FieldIdentifier"
    type: "TypeDescriptor"
    children: None


class ParameterDeclaration(AstNode):
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


class ParameterList(AstNode):
    field_names = []
    children: Optional[
        List[Union["Identifier", "ParameterDeclaration", "VariadicParameter"]]
    ]


class ParenthesizedDeclarator(AstNode):
    field_names = []
    children: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]


class ParenthesizedExpression(AstNode):
    field_names = []
    children: Union["_expression", "CommaExpression", "PreprocDefined"]


class PointerDeclarator(AstNode):
    field_names = ["declarator"]
    declarator: Union["_declarator", "_fieldDeclarator", "_typeDeclarator"]
    children: Optional[
        List[Union["MsBasedModifier", "MsPointerModifier", "TypeQualifier"]]
    ]


class PointerExpression(AstNode):
    field_names = ["argument", "operator"]
    argument: "_expression"
    operator: Union["str", "str"]
    children: None


class PreprocCall(AstNode):
    field_names = ["argument", "directive"]
    argument: Optional["PreprocArg"]
    directive: "PreprocDirective"
    children: None


class PreprocDef(AstNode):
    field_names = ["name", "value"]
    name: "Identifier"
    value: Optional["PreprocArg"]
    children: None


class PreprocDefined(AstNode):
    field_names = []
    children: "Identifier"


class PreprocElif(AstNode):
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


class PreprocElifdef(AstNode):
    field_names = ["alternative", "name"]
    alternative: Optional[Union["PreprocElif", "PreprocElse"]]
    name: "Identifier"
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


class PreprocElse(AstNode):
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


class PreprocFunctionDef(AstNode):
    field_names = ["name", "parameters", "value"]
    name: "Identifier"
    parameters: "PreprocParams"
    value: Optional["PreprocArg"]
    children: None


class PreprocIf(AstNode):
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


class PreprocIfdef(AstNode):
    field_names = ["alternative", "name"]
    alternative: Optional[Union["PreprocElif", "PreprocElifdef", "PreprocElse"]]
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


class PreprocInclude(AstNode):
    field_names = ["path"]
    path: Union["CallExpression", "Identifier", "StringLiteral", "SystemLibString"]
    children: None


class PreprocParams(AstNode):
    field_names = []
    children: Optional[List["Identifier"]]


class ReturnStatement(AstNode):
    field_names = []
    children: Optional[Union["_expression", "CommaExpression"]]


class SizedTypeSpecifier(AstNode):
    field_names = ["type"]
    type: Optional[Union["PrimitiveType", "TypeIdentifier"]]
    children: None


class SizeofExpression(AstNode):
    field_names = ["type", "value"]
    type: Optional["TypeDescriptor"]
    value: Optional["_expression"]
    children: None


class StorageClassSpecifier(AstNode):
    field_names = []
    children: None


class StringLiteral(AstNode):
    field_names = []
    children: Optional[List[Union["EscapeSequence", "StringContent"]]]


class StructSpecifier(AstNode):
    field_names = ["body", "name"]
    body: Optional["FieldDeclarationList"]
    name: Optional["TypeIdentifier"]
    children: Optional[List[Union["AttributeSpecifier", "MsDeclspecModifier"]]]


class SubscriptDesignator(AstNode):
    field_names = []
    children: "_expression"


class SubscriptExpression(AstNode):
    field_names = ["argument", "index"]
    argument: "_expression"
    index: "_expression"
    children: None


class SwitchStatement(AstNode):
    field_names = ["body", "condition"]
    body: "CompoundStatement"
    condition: "ParenthesizedExpression"
    children: None


class TranslationUnit(AstNode):
    field_names = []
    children: Optional[
        List[
            Union[
                "_typeSpecifier",
                "AttributedStatement",
                "BreakStatement",
                "CaseStatement",
                "CompoundStatement",
                "ContinueStatement",
                "Declaration",
                "DoStatement",
                "ExpressionStatement",
                "ForStatement",
                "FunctionDefinition",
                "GotoStatement",
                "IfStatement",
                "LabeledStatement",
                "LinkageSpecification",
                "PreprocCall",
                "PreprocDef",
                "PreprocFunctionDef",
                "PreprocIf",
                "PreprocIfdef",
                "PreprocInclude",
                "ReturnStatement",
                "SwitchStatement",
                "TypeDefinition",
                "WhileStatement",
            ]
        ]
    ]


class TypeDefinition(AstNode):
    field_names = ["declarator", "type"]
    declarator: List["_typeDeclarator"]
    type: "_typeSpecifier"
    children: Optional[List[Union["AttributeSpecifier", "TypeQualifier"]]]


class TypeDescriptor(AstNode):
    field_names = ["declarator", "type"]
    declarator: Optional["_abstractDeclarator"]
    type: "_typeSpecifier"
    children: Optional[List["TypeQualifier"]]


class TypeQualifier(AstNode):
    field_names = []
    children: None


class UnaryExpression(AstNode):
    field_names = ["argument", "operator"]
    argument: Union["_expression", "PreprocDefined"]
    operator: Union["str", "str", "str", "str"]
    children: None


class UnionSpecifier(AstNode):
    field_names = ["body", "name"]
    body: Optional["FieldDeclarationList"]
    name: Optional["TypeIdentifier"]
    children: Optional[List[Union["AttributeSpecifier", "MsDeclspecModifier"]]]


class UpdateExpression(AstNode):
    field_names = ["argument", "operator"]
    argument: "_expression"
    operator: Union["str", "str"]
    children: None


class VariadicParameter(AstNode):
    field_names = []
    children: None


class WhileStatement(AstNode):
    field_names = ["body", "condition"]
    body: "_statement"
    condition: "ParenthesizedExpression"
    children: None


class Character(AstNode):
    field_names = []
    children: None


class Comment(AstNode):
    field_names = []
    children: None


class EscapeSequence(AstNode):
    field_names = []
    children: None


class FalseBool(AstNode):
    field_names = []
    children: None


class FieldIdentifier(AstNode):
    field_names = []
    children: None


class Identifier(AstNode):
    field_names = []
    children: None


class MsRestrictModifier(AstNode):
    field_names = []
    children: None


class MsSignedPtrModifier(AstNode):
    field_names = []
    children: None


class MsUnsignedPtrModifier(AstNode):
    field_names = []
    children: None


class NumberLiteral(AstNode):
    field_names = []
    children: None


class PreprocArg(AstNode):
    field_names = []
    children: None


class PreprocDirective(AstNode):
    field_names = []
    children: None


class PrimitiveType(AstNode):
    field_names = []
    children: None


class StatementIdentifier(AstNode):
    field_names = []
    children: None


class StringContent(AstNode):
    field_names = []
    children: None


class SystemLibString(AstNode):
    field_names = []
    children: None


class TrueBool(AstNode):
    field_names = []
    children: None


class TypeIdentifier(AstNode):
    field_names = []
    children: None


class Operator(AstNode):
    field_names = []
    children: None


class Unnamed(AstNode):
    field_names = []
    children: None


class Whitespace(AstNode):
    def __init__(self, text: str):
        self.text = text
        self.id = None
        self.named_child_count = None
        self.named_children = None
        self.children_named_idxs = None
        self.base_node = None
        
    def get_text(self) -> str:
        return self.text

    field_names = []
    children: None


type_name_to_class = {
    "+": Operator,
    "-": Operator,
    "=": Operator,
    "^": Operator,
    "*": Operator,
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
    "alignof_expression": AlignofExpression,
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
    "else_clause": ElseClause,
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
    "generic_expression": GenericExpression,
    "gnu_asm_clobber_list": GnuAsmClobberList,
    "gnu_asm_expression": GnuAsmExpression,
    "gnu_asm_goto_list": GnuAsmGotoList,
    "gnu_asm_input_operand": GnuAsmInputOperand,
    "gnu_asm_input_operand_list": GnuAsmInputOperandList,
    "gnu_asm_output_operand": GnuAsmOutputOperand,
    "gnu_asm_output_operand_list": GnuAsmOutputOperandList,
    "gnu_asm_qualifier": GnuAsmQualifier,
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
    "null": Null,
    "offsetof_expression": OffsetofExpression,
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
    "preproc_elifdef": PreprocElifdef,
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
    "character": Character,
    "comment": Comment,
    "escape_sequence": EscapeSequence,
    "false": False,
    "field_identifier": FieldIdentifier,
    "identifier": Identifier,
    "ms_restrict_modifier": MsRestrictModifier,
    "ms_signed_ptr_modifier": MsSignedPtrModifier,
    "ms_unsigned_ptr_modifier": MsUnsignedPtrModifier,
    "number_literal": NumberLiteral,
    "preproc_arg": PreprocArg,
    "preproc_directive": PreprocDirective,
    "primitive_type": PrimitiveType,
    "statement_identifier": StatementIdentifier,
    "string_content": StringContent,
    "system_lib_string": SystemLibString,
    "true": True,
    "type_identifier": TypeIdentifier,
}
