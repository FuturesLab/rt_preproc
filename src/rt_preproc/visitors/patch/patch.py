import rt_preproc.parser.ast as ast
from typing import Optional, List, Any, Self
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from collections import defaultdict
import copy
from rt_preproc.visitors.patch.data import Macro, FuncDecl, VarDecl, VarIdent, MoveUpMsg
import rt_preproc.visitors.patch.ast_ext as ast_ext
import itertools


class PatchCtx(IVisitorCtx):
    def __init__(
        self,
        parent_ctx: Optional[Self] = None,
        parent: Optional[ast.AstNode] = None,
        in_ifdef: bool = False,
        ifdef_cond: Optional[Macro] = None,
        var_decls: dict[str, List[VarDecl]] = defaultdict(list),
    ) -> None:
        self.parent_ctx = parent_ctx
        self.parent = parent
        self.in_ifdef = in_ifdef or (parent_ctx is not None and parent_ctx.in_ifdef)
        self.ifdef_cond = ifdef_cond
        self.var_decls = var_decls

    def get_ifdef_cond_stack(self) -> List[Macro]:
        stack = []
        ctx = self
        while ctx is not None:
            if ctx.ifdef_cond is not None:
                stack.append(ctx.ifdef_cond)
            ctx = ctx.parent_ctx
        return stack

    def clone(self, parent: ast.AstNode) -> Self:
        return PatchCtx(
            parent_ctx=self.parent_ctx,
            parent=parent,
            in_ifdef=self.in_ifdef,  # readonly
            ifdef_cond=copy.deepcopy(self.ifdef_cond),
            var_decls=copy.deepcopy(self.var_decls),
        )


def update_if_marker(
    node: ast.AstNode,
    ctx: PatchCtx,
) -> ast.AstNode:
    """
    If the node is a marker, convert it to a true AST node.
    For example, VariableDeclarationMarker -> Declaration
    """
    if isinstance(node, ast_ext.Marker):
        if isinstance(node, ast_ext.VariableDeclarationMarker):
            return node.var_decl.convert_to_ast(ctx.var_decls)
        if isinstance(node, ast_ext.VariableUsageMarker):
            raise Exception("VariableUsageMarker unimplemented")
        else:
            raise Exception("Unexpected marker type")
    return node


class PatchVisitor(IVisitor):
    """Visitor for performing variability transformations on AST nodes."""

    def __init__(self) -> None:
        self.macros: dict[str, str] = {}
        self.structs: dict[str, ast.StructSpecifier] = {}
        self.fn_decls: dict[str, List[FuncDecl]] = defaultdict(list)
        self.move_to_mains: List[ast.AstNode] = []

    def build_setup_prelude(self) -> str:
        buf = ""
        buf += "#include <stdio.h>      /* printf */\n"
        buf += "#include <stdlib.h>     /* strtol */\n"
        buf += "#include <assert.h>     /* assert */\n\n"
        types = set(self.macros[m_name] for m_name in self.macros)

        # TODO: handle non-int data types
        for t in types:
            buf += f"#define UNDEFINED_{t.capitalize()} 0xdeadbeef\n"
        for m_name in self.macros:
            t = self.macros[m_name]
            buf += f"{t} {m_name} = UNDEFINED_{t.capitalize()};\n"

        buf += "\nint setup_env_vars() {\n"
        for m_name in self.macros:
            buf += f'  char* {m_name}_env_str = getenv("{m_name}");\n'
            buf += f"  if ({m_name}_env_str)"
            # TODO: handle non-int data types
            buf += f" {m_name} = strtol({m_name}_env_str, NULL, 10);\n"

        buf += "  return 0;\n"
        buf += "}\n\n"

        return buf

    def visit_children(
        self,
        node: ast.AstNode,
        ctx: PatchCtx,
    ) -> MoveUpMsg:
        move_up_all = MoveUpMsg()
        i = 0

        while i < len(node.children):
            up_msg: MoveUpMsg = node.children[i].accept(self, ctx.clone(node))
            move_up_all.var_idents.update(up_msg.var_idents)
            move_ups = up_msg.move_ups
            new_node = up_msg.node
            if ctx.in_ifdef:
                move_up_all.move_ups.extend(move_ups)
            elif len(move_ups) > 0:
                # for variable declarations, we need to add them to the ctx's var_decls dict
                for move_node in move_ups:
                    if isinstance(move_node, ast_ext.VariableDeclarationMarker):
                        ctx.var_decls[move_node.var_decl.name].append(
                            move_node.var_decl
                        )
                # since we are now out of the ifdef block, we need to convert the move_up nodes to
                # real AST nodes (in the case of VariableDeclarationMarker) and put them in the children list
                move_ups = [update_if_marker(node, ctx) for node in move_ups]
                node.children = node.children[:i] + move_ups + node.children[i:]
                i += len(move_ups)
            # a bit hacky, delete the semicolon after a call expression is converted to an if chain
            if isinstance(node.children[i], ast.CallExpression) and not isinstance(
                new_node, ast.CallExpression
            ):
                for j in range(i + 1, len(node.children)):
                    if node.children[j].text == ";":
                        node.children[j] = ast.Whitespace(" ")
                        break
            if new_node is not None:
                node.children[i] = new_node
            i += 1
        return move_up_all

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        assert len(up_msg.move_ups) == 0
        node.children.insert(0, ast.Custom(self.build_setup_prelude()))
        return MoveUpMsg(node, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.Identifier, ctx: PatchCtx) -> MoveUpMsg:
        return MoveUpMsg(node, var_idents=[node.text])

    @visit.register
    def _(self, node: ast.PreprocElse, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(
            node,
            PatchCtx(
                parent=node,
                in_ifdef=True,
                parent_ctx=ctx.parent_ctx,  # we skip the ctx of the ifdef to act like preproc else is on the same syntax level as the ifdef
                ifdef_cond=Macro(
                    ctx.ifdef_cond.name,
                    ctx.ifdef_cond.type,
                    def_cond=True,
                ),
            ),
        )
        return MoveUpMsg(node, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.PreprocIfdef, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(
            node,
            PatchCtx(
                parent=node,
                in_ifdef=True,
                parent_ctx=ctx,
                ifdef_cond=Macro(node.get_named_child(0).text, "int"),
            ),
        )

        identifier = node.get_named_child(0)
        self.macros[identifier.text] = "int"

        body_children = node.get_named_child(1).children
        # if the body is empty or all children are whitespace, then we can omit the ifdef
        if len(body_children) == 0 or all(
            isinstance(c, ast.Whitespace) for c in body_children
        ):
            return MoveUpMsg(ast.Custom("\n"), up_msg.move_ups)

        new_node = ast.IfStatement()
        new_node.children = [
            ast.Unnamed("if"),
            ast.Whitespace(" "),
            ast.Unnamed("("),
            node.get_named_child(0),
            ast.Unnamed("==" if ctx.ifdef_cond and ctx.ifdef_cond.def_cond else "!="),
            ast.Identifier("UNDEFINED_Int"),  # TODO: handle types other than int
            ast.Unnamed(")"),
            ast.Whitespace(" "),
            ast.Unnamed("{"),
            ast.Whitespace("\n"),
            node.get_named_child(1),
            ast.Whitespace("\n"),
            ast.Unnamed("}"),
            ast.Whitespace("\n"),
        ]
        if node.get_child_by_name("alternative") is not None:
            # TODO handle else if
            alt = node.get_child_by_name("alternative")
            if isinstance(alt, ast.PreprocElse):
                new_node.children.extend(
                    [
                        ast.Unnamed("else"),
                        ast.Whitespace(" "),
                        ast.Unnamed("{"),
                        ast.Whitespace("\n"),
                        alt.get_named_child(0),
                        ast.Whitespace("\n"),
                        ast.Unnamed("}"),
                        ast.Whitespace("\n"),
                    ]
                )
        if isinstance(ctx.parent, ast.TranslationUnit):
            # if this is a top level ifdef, we need to move what this would become to the main function
            self.move_to_mains.append(new_node)
            return MoveUpMsg(ast.Custom("\n"), up_msg.move_ups)
        # TODO: update children_named_idxs
        return MoveUpMsg(new_node, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.Declaration, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        if ctx.in_ifdef:
            # move this declaration up to the parent,
            #  but with UndefinedInt as the initializer
            # and modify this to be an assignment
            init_decl = node.get_named_child(1)
            name_node = None
            is_id = isinstance(init_decl, ast.Identifier)
            if is_id:
                name_node = init_decl
            else:
                name_node = init_decl.get_named_child(0)
            type_node = node.get_named_child(0)
            type_str = type_node.text
            macro_set = set(ctx.get_ifdef_cond_stack())
            move_up_node = ast_ext.VariableDeclarationMarker(
                VarDecl(
                    name_node.text,
                    type_str,
                    # TODO: handle other data types
                    ast.Identifier("UNDEFINED_Int"),
                    macro_set,
                )
            )
            up_msg.move_ups.append(move_up_node)
            new_node = None
            if not is_id:
                new_node = ast.AssignmentExpression()
                new_node.children = [
                    name_node,
                    ast.Unnamed("="),
                    init_decl.get_named_child(1),
                    ast.Unnamed(";"),
                    ast.Whitespace("\n"),
                ]
            return MoveUpMsg(new_node, up_msg.move_ups)
        else:
            return MoveUpMsg(None, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.FunctionDefinition, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)

        func_decl = node.get_named_child(1)
        func_name = func_decl.get_named_child(0).text
        self.fn_decls[func_name].append(
            FuncDecl(func_decl, set(ctx.get_ifdef_cond_stack()))
        )
        if len(self.fn_decls[func_name]) > 1:
            # if there are multiple function decls for this name, we need to give it a different name
            func_decl.set_named_child(
                0, ast.Custom(f"{func_name}_{len(self.fn_decls[func_name])}")
            )
            node.set_named_child(1, func_decl)
        if func_name == "main":
            setup_env_vars_run_str = r"""
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
            """
            body = node.get_named_child(2)
            for i in range(len(body.children)):
                if body.children[i].text == "{":
                    body.children.insert(i + 1, ast.Custom(setup_env_vars_run_str))
                    for j, move_node in enumerate(self.move_to_mains):
                        body.children.insert(i + 2 + j, move_node)
                    break
            else:
                raise Exception("No opening brace found in main function body")
            node.set_named_child(2, body)
            return MoveUpMsg(node, up_msg.move_ups)
        else:
            # if in ifdef block, move this function definition up to the parent
            if ctx.in_ifdef:
                # TODO: add an assertion to the body that the ifdef condition is true
                body = node.get_named_child(2)
                for i in range(len(body.children)):
                    if body.children[i].text == "{":
                        for cond_macro in ctx.get_ifdef_cond_stack():
                            body.children.insert(
                                i + 1,
                                ast.Custom(
                                    f"\nassert({cond_macro.name} {'==' if cond_macro.def_cond else '!='} UNDEFINED_{cond_macro.type.capitalize()});\n"
                                ),
                            )
                        break
                else:
                    raise Exception("No opening brace found for function body")
                body.children.append(ast.Whitespace("\n"))
                node.set_named_child(2, body)
                up_msg.move_ups.append(node)
                return MoveUpMsg(ast.Whitespace("\n"), up_msg.move_ups)

        return MoveUpMsg(None, up_msg.move_ups)

    # @visit.register
    # def _(self, node: ast.Declaration, ctx: PatchCtx) -> MoveUpMsg:
    #     # TODO: here is where we should also handle the magic of renaming variables based on their macro set
    #     raise Exception("Declaration unimplemented")

    @visit.register
    def _(self, node: ast.ExpressionStatement, ctx: PatchCtx) -> MoveUpMsg:
        # TODO: here is where we should handle the magic of renaming variables based on their macro set
        #
        up_msg = self.visit_children(node, ctx)

        rename_set: dict[str, List[VarIdent]] = defaultdict(list)
        ctx_macro_set = set(ctx.get_ifdef_cond_stack())
        for ident in up_msg.var_idents:
            # if the identifier is in the macro set, we'll need to duplicate and rename
            # let's gather up all the variable decls that match this identifier
            if ident in ctx.var_decls:
                for i, var_decl in enumerate(ctx.var_decls[ident]):
                    # we only need to rename in the case where a macro
                    # is in the var_decl's macro set that is not in the current ifdef cond stack
                    remainder_macro_set = var_decl.macro_set - ctx_macro_set
                    # TODO: move this renaming functionality into data.py
                    renamed_var_ident = VarIdent(
                        ident + "_" + str(i + 1) if i > 0 else ident,
                        remainder_macro_set,
                        orig_name=ident,
                    )
                    rename_set[ident].append(renamed_var_ident)
            # if there are none (in the case of left hand init declarators), we don't need to rename
            # so no need for an else case here

        # if the macro set is empty for all the variables, we don't need to do anything
        # without this, the code still works but emits extra if (1) {...} statements unnecessarily
        if all(
            all(len(var_ident.macro_set) == 0 for var_ident in var_idents)
            for var_idents in rename_set.values()
        ):
            return MoveUpMsg(None, up_msg.move_ups)

        # now for each of the combinations of renames, we need to duplicate the node and replace the identifiers
        out_node = ast.CompoundStatement()
        for i, combination in enumerate(itertools.product(*rename_set.values())):
            new_node = node.deepcopy()
            if not all(
                var_ident.orig_name == var_ident.name for var_ident in combination
            ):
                for var_ident in combination:
                    new_node.replace_ident(var_ident.orig_name, var_ident.name)

            # now add an if statement around it using the macros in combination
            if_statement = ast.IfStatement()
            if_statement.children = [
                ast.Unnamed("if" if i == 0 else "else if"),
                ast.Whitespace(" "),
                ast.Unnamed("("),
            ]
            # TODO: filter out incompatible macros
            for var_ident in combination:
                for cond_macro in var_ident.macro_set:
                    if_statement.children.extend(
                        [
                            ast.Whitespace(" "),
                            ast.Identifier(cond_macro.name),
                            ast.Whitespace(" "),
                            ast.Unnamed("==" if cond_macro.def_cond else "!="),
                            ast.Whitespace(" "),
                            # TODO: handle other data types
                            ast.Custom("UNDEFINED_Int"),
                            ast.Whitespace(" "),
                            ast.Unnamed("&&"),
                            ast.Whitespace(" "),
                        ]
                    )
            if_statement.children.append(ast.TrueBool("1"))
            if_statement.children.extend(
                [
                    ast.Unnamed(")"),
                    ast.Unnamed("{"),
                    ast.Whitespace("\n"),
                    new_node,
                    ast.Whitespace("\n"),
                    ast.Unnamed("}"),
                    ast.Whitespace("\n"),
                ]
            )
            else_clause = ast.ElseClause()
            else_clause.children = [
                ast.Unnamed("else"),
                ast.Whitespace(" "),
                ast.Unnamed("{"),
                ast.Whitespace("\n"),
                ast.Custom("assert(0);\n"),
                ast.Unnamed("}"),
                ast.Whitespace("\n"),
            ]
            if_statement.children.append(else_clause)
            out_node.children.append(if_statement)

        # we consumed the var_idents here so they don't get moved up
        return MoveUpMsg(out_node, up_msg.move_ups)

    # @visit.register
    # def _(self, node: ast.AssignmentExpression, ctx: PatchCtx) -> MoveUpMsg:
    #     up_msg = self.visit_children(node, ctx)
    #     if ctx.in_ifdef:
    #         # move this assignment up to the parent,
    #         #  but with UndefinedInt as the initializer
    #         # and modify this to be an assignment
    #         init_decl = node.get_named_child(1)
    #         name_node = None
    #         is_id = isinstance(init_decl, ast.Identifier)
    #         if is_id:
    #             name_node = init_decl
    #         else:
    #             name_node = init_decl.get_named_child(0)

    #         type_node = node.get_named_child(0)
    #         type_str = type_node.text
    #         macro_set = set(ctx.get_ifdef_cond_stack())
    #         move_up_node = ast_ext.VariableDeclarationMarker(
    #             VarDecl(
    #                 name_node.text,
    #                 type_str,

    #     return MoveUpMsg(None, up_msg.move_up)

    @visit.register
    def _(self, node: ast.CallExpression, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        fn_name = node.get_named_child(0).text
        if len(self.fn_decls[fn_name]) > 1:
            compound_stmt = ast.CompoundStatement()
            macro_set = set(ctx.get_ifdef_cond_stack())
            for i, fn_decl in enumerate(self.fn_decls[fn_name]):
                # switch on the ifdef conditions
                if_statement = ast.IfStatement()
                if_statement.children = [
                    ast.Unnamed("if" if i == 0 else "else if"),
                    ast.Unnamed("("),
                ]
                for cond_macro in fn_decl.macro_set:
                    if cond_macro in macro_set:
                        continue
                    if_statement.children.extend(
                        [
                            ast.Whitespace(" "),
                            ast.Identifier(cond_macro.name),
                            ast.Whitespace(" "),
                            ast.Unnamed("==" if cond_macro.def_cond else "!="),
                            ast.Whitespace(" "),
                            # TODO: handle other data types
                            ast.Identifier("UNDEFINED_Int"),
                            ast.Whitespace(" "),
                            ast.Unnamed("&&"),
                            ast.Whitespace(" "),
                        ]
                    )
                if_statement.children.append(ast.TrueBool("1"))
                new_node = node
                # if not the first function decl, we need to change the function name
                if i > 0:
                    new_node = ast.CallExpression()
                    new_node.children = [
                        ast.Identifier(node.get_named_child(0).text + "_" + str(i + 1)),
                        node.get_named_child(1),
                    ]
                if_statement.children.extend(
                    [
                        ast.Unnamed(")"),
                        ast.Unnamed("{"),
                        ast.Whitespace("\n"),
                        new_node,
                        ast.Unnamed(";"),
                        ast.Whitespace("\n"),
                        ast.Unnamed("}"),
                        ast.Whitespace("\n"),
                    ]
                )
                compound_stmt.children.append(if_statement)
            return MoveUpMsg(compound_stmt, up_msg.move_ups)
        else:
            return MoveUpMsg(node, up_msg.move_ups)

    # General expressions...
    @visit.register
    def _(self, node: ast.AstNode, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        return MoveUpMsg(None, up_msg.move_ups, up_msg.var_idents)
