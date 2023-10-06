import rt_preproc.parser.ast as ast
from typing import Optional, List, Any, Self
from multimethod import multimethod
from rt_preproc.visitors.base import IVisitor, IVisitorCtx


class Macro:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

class TransformCtx(IVisitorCtx):
    def __init__(
        self,
        parent_ctx: Optional[Self] = None,
        parent: Optional[ast.AstNode] = None,
        in_ifdef: bool = False,
        ifdef_cond: Optional[Macro] = None,
    ) -> None:
        self.parent_ctx = parent_ctx
        self.parent = parent
        self.in_ifdef = in_ifdef or (parent_ctx is not None and parent_ctx.in_ifdef)
        self.ifdef_cond = ifdef_cond

    def get_ifdef_cond_stack(self) -> List[Macro]:
        stack = []
        ctx = self
        while ctx is not None:
            if ctx.ifdef_cond is not None:
                stack.append(ctx.ifdef_cond)
            ctx = ctx.parent_ctx
        return stack




class TransformVisitor(IVisitor):
    """Visitor for performing variability transformations on AST nodes."""

    def __init__(self) -> None:
        self.macros: dict[str, str] = {}

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
        ctx: TransformCtx,
    ) -> list[Any]:
        move_up_all = []
        i = 0

        while i < len(node.children):
            new_node, move_up = node.children[i].accept(
                self,
                ctx,
            )
            if ctx.in_ifdef:
                move_up_all.extend(move_up)
            elif len(move_up) > 0:
                # put all the move_ups here in node.children
                node.children = node.children[:i] + move_up + node.children[i:]
                i += len(move_up)
            if new_node is not None:
                node.children[i] = new_node
            i += 1
        return move_up_all

    """Visitor functions below"""

    @multimethod
    def visit(self, node: ast.TranslationUnit, ctx: TransformCtx) -> Any:
        move_up = self.visit_children(node, ctx)
        assert len(move_up) == 0
        node.children.insert(0, ast.Custom(self.build_setup_prelude()))
        return node, []

    @visit.register
    def _(self, node: ast.PreprocIfdef, ctx: TransformCtx) -> Any:
        move_up = self.visit_children(
            node,
            TransformCtx(
                parent=node, 
                in_ifdef=True, 
                parent_ctx=ctx, 
                ifdef_cond=Macro(node.get_named_child(0).text, "int")
            ),
        )

        identifier = node.get_named_child(0)
        self.macros[identifier.text] = "int"

        body_children = node.get_named_child(1).children
        # if the body is empty or all children are whitespace, then we can omit the ifdef
        if len(body_children) == 0 or all(isinstance(c, ast.Whitespace) for c in body_children):
            return ast.Custom("\n"), move_up

        new_node = ast.IfStatement()
        new_node.children = [
            ast.Unnamed("if"),
            ast.Whitespace(" "),
            ast.Unnamed("("),
            node.get_named_child(0),
            ast.Unnamed("!="),
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
        # TODO: update children_named_idxs
        return new_node, move_up

    @visit.register
    def _(self, node: ast.Declaration, ctx: TransformCtx) -> Any:
        move_up = self.visit_children(node, ctx)
        if ctx.in_ifdef:
            # move this declaration up to the parent,
            #  but with UndefinedInt as the initializer
            # and modify this to be an assignment
            init_decl = node.get_named_child(1)

            move_up_node = ast.Declaration()
            move_up_node.children = [
                node.get_named_child(0),
                ast.Unnamed(" "),
                init_decl.get_named_child(0),
                ast.Unnamed(" = "),
                ast.Identifier("UNDEFINED_Int"),  # TODO: handle other data types
                ast.Unnamed(";"),
                ast.Whitespace("\n"),
            ]
            move_up.append(move_up_node)
            new_node = ast.AssignmentExpression()
            new_node.children = [
                init_decl.get_named_child(0),
                ast.Unnamed("="),
                init_decl.get_named_child(1),
                ast.Unnamed(";"),
                ast.Whitespace("\n"),
            ]
            return new_node, move_up
        else:
            return None, move_up

    @visit.register
    def _(self, node: ast.FunctionDefinition, ctx: TransformCtx) -> Any:
        move_up = self.visit_children(node, ctx)

        func_decl = node.get_named_child(1)
        func_name = func_decl.get_named_child(0).text
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
                    break
            else:
                raise Exception("No opening brace found in main function body")
            node.set_named_child(2, body)
            return node, move_up
        else:
            # if in ifdef block, move this function definition up to the parent
            if ctx.in_ifdef:
                # TODO: add an assertion to the body that the ifdef condition is true
                body = node.get_named_child(2)
                for i in range(len(body.children)):
                    if body.children[i].text == "{":
                        for cond_macro in ctx.get_ifdef_cond_stack():
                            body.children.insert(i + 1, 
                                ast.Custom(f"\nassert({cond_macro.name} != UNDEFINED_{cond_macro.type.capitalize()});\n"))
                        break
                else:
                    raise Exception("No opening brace found for function body")
                node.set_named_child(2, body)
                move_up.append(node)
                return ast.Whitespace("\n"), move_up

        return None, move_up

    # General expressions...
    @visit.register
    def _(self, node: ast.AstNode, ctx: TransformCtx) -> Any:
        move_up = self.visit_children(node, ctx)
        return None, move_up
