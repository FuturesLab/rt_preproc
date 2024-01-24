import rt_preproc.parser.ast as ast
from typing import Optional, List, Any, Self, Set, Union
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx
from collections import defaultdict
import copy
from rt_preproc.visitors.patch.data import (
    Macro,
    FuncDecl,
    VarDecl,
    DefDecl,
    DefFnDecl,
    VarIdent,
    MoveUpMsg,
)
import rt_preproc.visitors.patch.ast_ext as ast_ext
import itertools

setup_env_vars_run_str = r"""
  if (setup_env_vars() != 0) {
    printf("Error setting up environment variables\n");
    return 1;
  }
            """


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
        """
        Returns a list of the ifdef conditions that are currently active at this this context's scope.
        """
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
        elif isinstance(node, ast_ext.PreprocDefinitionMarker):
            return node.def_decl.convert_to_ast()
        elif isinstance(node, ast_ext.VariableUsageMarker):
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
        self.defines: dict[str, List[Union[DefDecl, DefFnDecl]]] = defaultdict(list)

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
                    elif isinstance(move_node, ast_ext.PreprocDefinitionMarker):
                        # Now this is done in the PreprocDef visitor itself to handle the parent-child relationship
                        # of the preproc ifdef + else
                        # This would be run after the ifdef AND else, but we need it to run after the ifdef (so else would catch it)
                        # self.defines[move_node.def_decl.name].append(move_node.def_decl)
                        pass

                # since we are now out of the ifdef block, we need to convert the move_up nodes to
                # real AST nodes (in the case of VariableDeclarationMarker) and put them in the children list
                move_ups = [update_if_marker(node, ctx) for node in move_ups]
                node.children = node.children[:i] + move_ups + node.children[i:]
                i += len(move_ups)
            # a bit hacky, delete the semicolon after a call expression is converted to an if chain
            if (
                isinstance(node.children[i], ast.CallExpression)
                and new_node != None
                and not isinstance(new_node, ast.CallExpression)
            ):
                for j in range(i + 1, len(node.children)):
                    if node.children[j].text == ";":
                        node.children[j] = ast.Whitespace(" ")
                        break
            if new_node is not None:
                node.children[i] = new_node
            i += 1
        return move_up_all

    def build_rename_dict(
        self, ctx: PatchCtx, var_idents: Set[str]
    ) -> dict[str, List[VarIdent]]:
        """
        Builds a rename dictionary for the given variable identifiers.
        The rename dictionary maps the original variable identifier to a list of renamed variable identifiers, one entry for each possible rename.
        Multiple renames are possible in the case of multiple ifdef conditions that refer to the same variable identifier.
        We also restrict the possibilities to the set of ifdef conditions that are not already in the current ifdef cond stack.
        """
        rename_dict: dict[str, List[VarIdent]] = defaultdict(list)
        ctx_macro_set = set(ctx.get_ifdef_cond_stack())
        for ident in var_idents:
            # if the identifier is in the macro set, we'll need to duplicate and rename
            # let's gather up all the variable decls that match this identifier
            if ident in ctx.var_decls:
                for i, var_decl in enumerate(ctx.var_decls[ident]):
                    # we only need to rename in the case where a macro
                    # is in both the current ifdef cond stack and the variable decl's macro set
                    remainder_macro_set = var_decl.macro_set - ctx_macro_set

                    # TODO: move this renaming functionality into data.py
                    renamed_var_ident = VarIdent(
                        ident + "_" + str(i + 1) if i > 0 else ident,
                        remainder_macro_set,
                        orig_name=ident,
                    )
                    rename_dict[ident].append(renamed_var_ident)
            # if there are none (in the case of left hand init declarators), we don't need to rename
            # so no need for an else case here

        # handle function identifiers here too
        for ident in var_idents:
            for i, fn_decl in enumerate(self.fn_decls[ident]):
                remainder_macro_set = fn_decl.macro_set - ctx_macro_set
                renamed_var_ident = VarIdent(
                    ident + "_" + str(i + 1) if i > 0 else ident,
                    remainder_macro_set,
                    orig_name=ident,
                )
                rename_dict[ident].append(renamed_var_ident)

        for ident in self.defines:
            for i, def_decl in enumerate(self.defines[ident]):
                remainder_macro_set = def_decl.macro_set - ctx_macro_set
                renamed_var_ident = VarIdent(
                    ident + "_" + str(i + 1) if i > 0 else ident,
                    remainder_macro_set,
                    orig_name=ident,
                )
                rename_dict[ident].append(renamed_var_ident)
        return rename_dict

    def multiversal_duplication(
        self,
        node: ast.AstNode,
        ctx: PatchCtx,
        up_msg: MoveUpMsg,
        rename_dict: dict[str, List[VarIdent]] = None,
    ) -> ast.AstNode:
        """
        This function performs multiversal duplication on a node.
        It returns a new node that is the result of duplicating the node
        with changes to the variable identifiers
        for each combination of ifdef conditions that are not in the current ifdef cond stack.

        If there are no variable identifiers that need to be renamed, this function returns None.
        """
        if rename_dict is None:
            rename_dict = self.build_rename_dict(ctx, up_msg.var_idents)
        # if the macro set is empty for all the variables, we don't need to do anything
        # without this, the code still works but emits extra if (1) {...} statements unnecessarily
        if all(
            all(len(var_ident.macro_set) == 0 for var_ident in var_idents)
            for var_idents in rename_dict.values()
        ):
            return None

        # now for each of the combinations of renames, we need to duplicate the node and replace the identifiers
        out_node = ast.CompoundStatement()
        for i, combination in enumerate(itertools.product(*rename_dict.values())):
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
            out_node.children.append(if_statement)

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
        out_node.children.append(else_clause)

        return out_node

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
    def _(self, node: ast.PreprocDef, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        if ctx.in_ifdef:
            orig_name = node.get_named_child(0).text
            name = orig_name
            if name in self.defines:
                # if there is already a definition for this macro, we need to rename it
                name = name + "_" + str(len(self.defines[name]) + 1)
            def_decl = DefDecl(
                name,
                node.get_named_child(1).text,
                set(ctx.get_ifdef_cond_stack()),
                orig_name=orig_name,
            )
            self.defines[orig_name].append(def_decl)

            up_msg.move_ups.append(ast_ext.PreprocDefinitionMarker(def_decl))
            return MoveUpMsg(ast.Whitespace("\n"), up_msg.move_ups)
        return MoveUpMsg(node, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.PreprocFunctionDef, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        if ctx.in_ifdef:
            orig_name = node.get_named_child(0).text
            name = orig_name
            if name in self.defines:
                # if there is already a definition for this macro, we need to rename it
                name = name + "_" + str(len(self.defines[name]) + 1)

            def_fn_decl = DefFnDecl(
                name,
                node.get_named_child(1),
                node.get_named_child(2).text,
                set(ctx.get_ifdef_cond_stack()),
                orig_name=orig_name,
            )
            self.defines[orig_name].append(def_fn_decl)

            up_msg.move_ups.append(ast_ext.PreprocDefinitionMarker(def_fn_decl))
            return MoveUpMsg(ast.Whitespace("\n"), up_msg.move_ups)
        return MoveUpMsg(node, up_msg.move_ups)

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

        # ifdefs don't put all the body in a compound statement, they are just directly in the node children
        # so body children starts after the identifier, and ends before the #else or #endif
        start_idx = node.children_named_idxs.index(0) + 1
        end_idx = next(
            i
            for i, child in enumerate(node.children)
            if isinstance(child, ast.PreprocElse)
            or isinstance(child, ast.PreprocElifdef)
            or isinstance(child, ast.PreprocElif)
            or (isinstance(child, ast.Unnamed) and child.text == "#endif")
        )
        body_children = node.children[start_idx:end_idx]

        # if the body is empty or all children are whitespace, then we can omit the ifdef
        if len(body_children) == 0 or all(
            isinstance(c, ast.Whitespace) for c in body_children
        ):
            return MoveUpMsg(ast.Whitespace("\n"), up_msg.move_ups)

        body_block = ast.CompoundStatement()
        body_block.children = body_children

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
            body_block,
            ast.Unnamed("}"),
            ast.Whitespace("\n"),
        ]
        # TODO: this will not work if we don't handle the named children modification correctly
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
                        alt.get_named_child(
                            0
                        ),  # FIXME: do something similar to the body children above
                        ast.Whitespace("\n"),
                        ast.Unnamed("}"),
                        ast.Whitespace("\n"),
                    ]
                )
        if isinstance(ctx.parent, ast.TranslationUnit):
            # if this is a top level ifdef, we need to move what this would become to the main function
            self.move_to_mains.append(new_node)
            return MoveUpMsg(ast.Whitespace("\n"), up_msg.move_ups)
        # TODO: update children_named_idxs
        return MoveUpMsg(new_node, up_msg.move_ups)

    @visit.register
    def _(self, node: ast.Declaration, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        init_decl = node.get_named_child(1)
        name_node = None
        is_id = isinstance(init_decl, ast.Identifier)
        if is_id:
            name_node = init_decl
        else:
            name_node = init_decl.get_named_child(0)
        type_node = node.get_named_child(0)
        type_str = type_node.text
        if ctx.in_ifdef:
            # move this declaration up to the parent,
            # but with UndefinedInt as the initializer
            # and modify this to be an assignment
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

            # if it wasn't an identifier, then the declaration was an init declarator
            if isinstance(init_decl, ast.InitDeclarator):
                init_rhs = init_decl.get_named_child(1)

                new_node = ast.AssignmentExpression()
                new_node.children = [
                    name_node,
                    ast.Unnamed("="),
                    init_rhs,
                    ast.Unnamed(";"),
                    ast.Whitespace("\n"),
                ]
                dup_node = self.multiversal_duplication(new_node, ctx, up_msg)
                if dup_node is not None:
                    new_node = dup_node

            return MoveUpMsg(new_node, up_msg.move_ups)
        elif isinstance(init_decl, ast.InitDeclarator):
            # if this is an init declarator, ie: int x = 5;
            # we need to check if there is variability in the initializer
            # if there is, we need to convert this to a compound statement
            # with a declaration to UndefinedInt
            # and then add the assignments for each combination of ifdef conditions
            init_rhs = init_decl.get_named_child(1)

            rename_dict = self.build_rename_dict(ctx, up_msg.var_idents)
            has_variability = not all(
                all(len(var_ident.macro_set) == 0 for var_ident in var_idents)
                for var_idents in rename_dict.values()
            )
            if has_variability:
                macro_set = set(ctx.get_ifdef_cond_stack())
                undef_decl = VarDecl(
                    name_node.text,
                    type_str,
                    # TODO: handle other data types
                    ast.Identifier("UNDEFINED_Int"),
                    macro_set,
                )
                compound_stmt = ast.CompoundStatement()
                compound_stmt.children = [
                    undef_decl.convert_to_ast(ctx.var_decls),
                ]

                assign_node = ast.AssignmentExpression()
                assign_node.children = [
                    name_node,
                    ast.Unnamed("="),
                    init_rhs,
                    ast.Unnamed(";"),
                    ast.Whitespace("\n"),
                ]
                dup_assigns = self.multiversal_duplication(
                    assign_node, ctx, up_msg, rename_dict=rename_dict
                )
                if dup_assigns is not None:
                    compound_stmt.children.append(dup_assigns)
                else:
                    compound_stmt.children.append(assign_node)
                return MoveUpMsg(compound_stmt, up_msg.move_ups)
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

    @visit.register
    def _(self, node: ast.ExpressionStatement, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        # Here is where we handle the magic of renaming variables based on their macro set

        out_node = self.multiversal_duplication(node, ctx, up_msg)

        # we consumed the var_idents here so they don't get moved up
        return MoveUpMsg(out_node, up_msg.move_ups)

    # General expressions...
    @visit.register
    def _(self, node: ast.AstNode, ctx: PatchCtx) -> MoveUpMsg:
        up_msg = self.visit_children(node, ctx)
        return MoveUpMsg(None, up_msg.move_ups, up_msg.var_idents)
