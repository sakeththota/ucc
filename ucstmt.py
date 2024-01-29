"""
ucstmt.py.

This file contains definitions of AST nodes that represent uC
statements.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

from dataclasses import dataclass
from typing import List, Optional
from ucbase import ASTNode
from ucerror import error
from ucexpr import ExpressionNode
# import uctypes


@dataclass
class StatementNode(ASTNode):
    """The base class for all statement nodes."""

    # add your code below if necessary


@dataclass
class BlockNode(ASTNode):
    """An AST node representing a block of statements.

    statements is a list of statement nodes.
    """

    statements: List[StatementNode]

    # add your code below if necessary
    def gen_function_defs(self, ctx):
        """Generate function defs."""
        for child in self.statements:
            ctx.print(indent=True, end="")
            child.gen_function_defs(ctx)


@dataclass
class IfNode(StatementNode):
    """An AST node representing an if statement.

    test is the condition, then_block is a block representing the then
    case, and else_block is a block representing the else case.
    """

    test: ExpressionNode
    then_block: BlockNode
    else_block: BlockNode

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if self.test.type.name != 'boolean':
            error(6, self.position,
                  f"type of test expression must be boolean,\
                       but was given {self.test.type.name}")

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("if (", end="")
        self.test.gen_function_defs(ctx)
        ctx.print(") {")
        new_ctx = ctx.clone()
        new_ctx.indent += "  "
        self.then_block.gen_function_defs(new_ctx)
        ctx.print("}", indent=True, end="")
        ctx.print(" else {")
        self.else_block.gen_function_defs(new_ctx)
        ctx.print("}", indent=True)


@dataclass
class WhileNode(StatementNode):
    """An AST node representing a while statement.

    test is the condition and body is a block representing the body.
    """

    test: ExpressionNode
    body: BlockNode

    # add your code below
    def basic_control(self, ctx):
        """Check basic control flow within this AST node."""
        new_ctx = ctx.clone()
        new_ctx['in_loop'] = True
        super().basic_control(new_ctx)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if self.test.type.name != 'boolean':
            error(6, self.position,
                  f"type of test expression must be boolean,\
                       but was given {self.test.type.name}")

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("while (", end="")
        self.test.gen_function_defs(ctx)
        ctx.print(") {")
        new_ctx = ctx.clone()
        new_ctx.indent += "  "
        self.body.gen_function_defs(new_ctx)
        ctx.print("}", indent=True)


@dataclass
class ForNode(StatementNode):
    """An AST node representing a for statement.

    init is the initialization, test is the condition, update is the
    update expression, and body is a block representing the body.
    init, test, and update may be None if the corresponding expression
    is omitted.
    """

    init: Optional[ExpressionNode]
    test: Optional[ExpressionNode]
    update: Optional[ExpressionNode]
    body: BlockNode

    # add your code below
    def basic_control(self, ctx):
        """Check basic control flow within this AST node."""
        new_ctx = ctx.clone()
        new_ctx['in_loop'] = True
        super().basic_control(new_ctx)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if self.test and self.test.type.name != 'boolean':
            error(6, self.position,
                  f"type of test expression must be boolean,\
                       but was given {self.test.type.name}")

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("for (", end="")
        self.init.gen_function_defs(ctx)
        ctx.print("; ", end="")
        self.test.gen_function_defs(ctx)
        ctx.print("; ", end="")
        self.update.gen_function_defs(ctx)
        ctx.print(") {")
        new_ctx = ctx.clone()
        new_ctx.indent += "  "
        self.body.gen_function_defs(new_ctx)
        ctx.print("}", indent=True)


@dataclass
class BreakNode(StatementNode):
    """An AST node representing a break statement."""

    # add your code below
    def basic_control(self, ctx):
        """Check basic control flow within this AST node."""
        if not ctx['in_loop']:
            error(5, self.position, "break statement must occur within a loop")
        super().basic_control(ctx)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("break;")


@dataclass
class ContinueNode(StatementNode):
    """An AST node representing a continue statement."""

    # add your code below
    def basic_control(self, ctx):
        """Check basic control flow within this AST node."""
        if not ctx['in_loop']:
            error(5, self.position, "continue statement\
                 must occur within a loop")
        super().basic_control(ctx)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("continue;")


@dataclass
class ReturnNode(StatementNode):
    """An AST node representing a return statement.

    expr is the return expression if there is one, None otherwise.
    """

    expr: Optional[ExpressionNode]

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if ctx['rettype'] == 'void' and self.expr:
            error(6, self.position,
                  "function should not have \
                      a return expression as it's return type is void")
        elif self.expr and ctx['rettype'] != self.expr.type:
            error(6, self.position,
                  f"function requires return type {ctx['rettype']} \
                             but got {self.expr.type.name}")

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("return ", end="")
        if self.expr:
            self.expr.gen_function_defs(ctx)
        ctx.print(";")


@dataclass
class ExpressionStatementNode(StatementNode):
    """An AST node representing a statement of just an expression.

    expr is the expression.
    """

    expr: ExpressionNode

    # add your code below if necessary
    def gen_function_defs(self, ctx):
        """Generate function defs."""
        super().gen_function_defs(ctx)
        ctx.print(";")
