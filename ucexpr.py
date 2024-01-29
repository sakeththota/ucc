"""
ucexpr.py.

This file contains definitions of AST nodes that represent uC
expressions.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

from dataclasses import dataclass
from typing import List, Optional
from ucbase import attribute
import ucbase
from ucerror import error
import ucfunctions
import uctypes


#############################
# Base Node for Expressions #
#############################

@dataclass
class ExpressionNode(ucbase.ASTNode):
    """The base class for all nodes representing expressions.

    type is a reference to the computed uctypes.Type of this
    expression.
    """

    type: Optional[uctypes.Type] = attribute()

    @staticmethod
    def is_lvalue():
        """Return whether or not this node produces an l-value."""
        return False

    # add your code below if necessary

############
# Literals #
############


@dataclass
class LiteralNode(ExpressionNode):
    """The base class for all nodes representing literals.

    text is the textual representation of the literal for code
    generation.
    """

    text: str

    # add your code below if necessary
    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(self.text, end="")


@dataclass
class IntegerNode(LiteralNode):
    """An AST node representing an integer (int or long) literal."""

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        typestr = 'long' if self.text[-1] == 'l'\
            or self.text[-1] == 'L' else 'int'
        self.type = ctx.global_env.lookup_type(6, self.position, typestr)


@dataclass
class FloatNode(LiteralNode):
    """An AST node representing a float literal."""

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        self.type = ctx.global_env.lookup_type(6, self.position, 'float')


@dataclass
class StringNode(LiteralNode):
    """An AST node representing a string literal."""

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        self.type = ctx.global_env.lookup_type(6, self.position, 'string')

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(f"{self.text}s", end="")


@dataclass
class BooleanNode(LiteralNode):
    """An AST node representing a boolean literal."""

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        self.type = ctx.global_env.lookup_type(6, self.position, 'boolean')


@dataclass
class NullNode(LiteralNode):
    """An AST node representing the null literal."""

    text: str = 'nullptr'

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        self.type = ctx.global_env.lookup_type(6, self.position, 'null')


###################
# Name Expression #
###################

@dataclass
class NameExpressionNode(ExpressionNode):
    """An AST node representing a name expression.

    name is an AST node denoting the actual name.
    """

    name: ucbase.NameNode

    # add your code below
    @staticmethod
    def is_lvalue():
        """Return whether or not this node produces an l-value."""
        return True

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        self.type = ctx['local_env'].get_type(
            6, self.position, self.name.raw)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(f"UC_VAR({self.name.raw})", end="")

#######################
# Calls and Accessors #
#######################


@dataclass
class CallNode(ExpressionNode):
    """An AST node representing a function-call expression.

    name is an AST node representing the name of the function and args
    is a list of argument expressions to the function. func is a
    reference to the ucfunctions.Function named by this call.
    """

    name: ucbase.NameNode
    args: List[ExpressionNode]
    func: Optional[ucfunctions.Function] = attribute()

    # add your code below
    def resolve_calls(self, ctx):
        """Match function calls to the actual functions they name.

        Uses ctx.global_env to look up a function name. Reports an
        error if an unknown function is named.
        """
        self.func = ctx.global_env.lookup_function(
            3, self.position, self.name.raw)
        super().resolve_calls(ctx)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        self.func.check_args(6, self.position, self.args)
        self.type = self.func.rettype

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(f"UC_FUNCTION({self.name.raw})", end="")
        ctx.print("(", end="")
        for i, arg in enumerate(self.args):
            arg.gen_function_defs(ctx)
            if i != len(self.args)-1:
                ctx.print(", ", end="")
        ctx.print(")", end="")


@dataclass
class NewNode(ExpressionNode):
    """An AST node representing a new expression for a simple object.

    name is an AST node representing the type of the object and args
    is a list of argument expressions to the constructor.
    """

    name: ucbase.NameNode
    args: List[ExpressionNode]

    # add your code below
    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        super().resolve_types(ctx)
        self.type = ctx.global_env.lookup_type(
            2, self.position, self.name.raw)
        if isinstance(self.type, uctypes.PrimitiveType):
            error(2, self.position,
                  "simple allocations of primitives are not allowed")

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        self.type.check_args(6, self.position, self.args)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(f"uc_make_object<{self.type.mangle()}>", end="")
        ctx.print("(", end="")
        for i, arg in enumerate(self.args):
            arg.gen_function_defs(ctx)
            if i != len(self.args)-1:
                ctx.print(", ", end="")
        ctx.print(")", end="")


@dataclass
class NewArrayNode(ExpressionNode):
    """An AST node representing a new expression for an array.

    elem_type is a node representing the element type and args is a
    list of argument expressions representing the initial elements of
    the array.
    """

    elem_type: ucbase.BaseTypeNameNode
    args: List[ExpressionNode]

    # add your code below
    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        super().resolve_types(ctx)
        self.type = self.elem_type.type.array_type

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        self.type.check_args(6, self.position, self.args)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(
            f"uc_make_array_of<{self.elem_type.type.mangle()}>", end="")
        ctx.print("(", end="")
        for i, arg in enumerate(self.args):
            arg.gen_function_defs(ctx)
            if i != len(self.args)-1:
                ctx.print(", ", end="")
        ctx.print(")", end="")


@dataclass
class FieldAccessNode(ExpressionNode):
    """An AST node representing access to a field of an object.

    receiver is an expression representing the object whose field is
    being accessed and field is is an AST node representing the name
    of the field.
    """

    receiver: ExpressionNode
    field: ucbase.NameNode

    # add your code below
    def is_lvalue(self):
        """Return whether or not this node produces an l-value."""
        if isinstance(self.receiver.type, uctypes.ArrayType):
            return False
        return True

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if isinstance(self.receiver.type, uctypes.PrimitiveType)\
                and not isinstance(self.receiver.type, uctypes.ArrayType):
            error(6, self.position,
                  "receiver must be user-defined type or array type, "
                  + f"but was {self.receiver.type}")
            self.type = ctx.global_env.lookup_type(6, self.position, 'int')
        else:
            self.type = self.receiver.type.lookup_field(
                6, self.position, self.field.raw, ctx.global_env)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        if self.field.raw == "length":
            ctx.print("uc_length_field(", end="")
            self.receiver.gen_function_defs(ctx)
            ctx.print(")", end="")
        else:
            self.receiver.gen_function_defs(ctx)
            ctx.print(f"->UC_VAR({self.field.raw})", end="")


@dataclass
class ArrayIndexNode(ExpressionNode):
    """An AST node representing indexing into an array.

    receiver is an expression representing the array and index the
    index expression.
    """

    receiver: ExpressionNode
    index: ExpressionNode

    # add your code below
    @staticmethod
    def is_lvalue():
        """Return whether or not this node produces an l-value."""
        return True

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not isinstance(self.receiver.type, uctypes.ArrayType):
            error(6, self.position,
                  f"cannot index into non-array type {self.receiver.type}")
            self.type = ctx.global_env.lookup_type(6, self.position, 'int')
        elif self.index.type.name != 'int':
            error(6, self.position,
                  "array index expects type int, "
                  + f"but got type {self.index.type}")
            self.type = ctx.global_env.lookup_type(6, self.position, 'int')
        else:
            self.type = self.receiver.type.elem_type

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("uc_array_index(", end="")
        self.receiver.gen_function_defs(ctx)
        ctx.print(", ", end="")
        self.index.gen_function_defs(ctx)
        ctx.print(")", end="")

#####################
# Unary Expressions #
#####################


@dataclass
class UnaryPrefixNode(ExpressionNode):
    """A base AST node that represents a unary prefix operation.

    expr is the expression to which the operation is being applied and
    op_name is the string representation of the operator.
    """

    expr: ExpressionNode
    op_name: str

    # add your code below if necessary
    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print(self.op_name, end="")
        ctx.print("(", end="")
        self.expr.gen_function_defs(ctx)
        ctx.print(")", end="")


@dataclass
class PrefixSignNode(UnaryPrefixNode):
    """A base AST node representing a prefix sign operation."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not uctypes.is_numeric_type(self.expr.type):
            error(6, self.position,
                  "subexpression given is of type " +
                  f"{self.expr.type.name}, but must be numeric")
        self.type = self.expr.type


@dataclass
class PrefixPlusNode(PrefixSignNode):
    """An AST node representing a prefix plus operation."""

    op_name: str = '+'

    # add your code below if necessary


@dataclass
class PrefixMinusNode(PrefixSignNode):
    """An AST node representing a prefix minus operation."""

    op_name: str = '-'

    # add your code below if necessary


@dataclass
class NotNode(UnaryPrefixNode):
    """An AST node representing a not operation."""

    op_name: str = '!'

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if self.expr.type.name != 'boolean':
            error(6, self.position,
                  "subexpression given is of type "
                  + f"{self.expr.type.name}, but must be boolean")
        self.type = self.expr.type


@dataclass
class PrefixIncrDecrNode(UnaryPrefixNode):
    """A base AST node representing a prefix {in,de}crement operation."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not (self.expr.is_lvalue() and
                uctypes.is_numeric_type(self.expr.type)):
            error(6, self.position,
                  "subexpression must be a numeric l-value")
        self.type = self.expr.type


@dataclass
class PrefixIncrNode(PrefixIncrDecrNode):
    """An AST node representing a prefix increment operation."""

    op_name: str = '++'

    # add your code below if necessary


@dataclass
class PrefixDecrNode(PrefixIncrDecrNode):
    """An AST node representing a prefix decrement operation.

    expr is the operand expression.
    """

    op_name: str = '--'

    # add your code below if necessary


@dataclass
class IDNode(UnaryPrefixNode):
    """An AST node representing an id operation."""

    op_name: str = '#'

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if isinstance(self.expr.type, uctypes.PrimitiveType)\
                and not isinstance(self.expr.type, uctypes.ArrayType):
            error(6, self.position,
                  "subexpression was of type "
                  + f"{self.expr.type}, but must be of reference type")
        self.type = ctx.global_env.lookup_type(6, self.position, 'long')

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("uc_id(", end="")
        self.expr.gen_type_defs(ctx)
        ctx.print(")", end="")

######################
# Binary Expressions #
######################

# Base classes


@dataclass
class BinaryOpNode(ExpressionNode):
    """A base AST node that represents a binary infix operation.

    lhs is the left-hand side expression, rhs is the right-hand side
    expression, and op_name is the name of the operator.
    """

    lhs: ExpressionNode
    rhs: ExpressionNode
    op_name: str

    # add your code below if necessary
    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("(", end="")
        self.lhs.gen_function_defs(ctx)
        ctx.print(")", end="")
        ctx.print(f" {self.op_name} ", end="")
        ctx.print("(", end="")
        self.rhs.gen_function_defs(ctx)
        ctx.print(")", end="")


@dataclass
class BinaryArithNode(BinaryOpNode):
    """A base AST node representing a binary arithmetic operation."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if self.op_name != '+' and not \
                (uctypes.is_numeric_type(self.lhs.type)
                 and uctypes.is_numeric_type(self.rhs.type)):
            error(6, self.position, "lhs and rhs must be of numeric type")
        self.type = uctypes.join_types(
            6, self.position, self.lhs.type, self.rhs.type, ctx.global_env)


@dataclass
class BinaryLogicNode(BinaryOpNode):
    """A base AST node representing a binary logic operation."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not (self.lhs.type.name == 'boolean' and
                self.rhs.type.name == 'boolean'):
            error(6, self.position, "lhs and rhs operands"
                  + " must be of type boolean")
        self.type = ctx.global_env.lookup_type(6, self.position, 'boolean')


@dataclass
class BinaryCompNode(BinaryOpNode):
    """A base AST node representing binary comparison operation."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not ((uctypes.is_numeric_type(self.lhs.type)
                and uctypes.is_numeric_type(self.rhs.type))
                or (self.lhs.type.name == 'string'
                    and self.rhs.type.name == 'string')):
            error(6, self.position,
                  "lhs and rhs must be both numeric or both strings")
        self.type = ctx.global_env.lookup_type(6, self.position, 'boolean')


@dataclass
class EqualityTestNode(BinaryOpNode):
    """A base AST node representing an equality comparison."""

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        # compute lhs and rhs types
        super().type_check(ctx)
        # types arent the same or implicitly convertible
        if not uctypes.is_compatible(self.lhs.type, self.rhs.type) \
                and not uctypes.is_compatible(self.rhs.type, self.lhs.type):
            error(6, self.position, "lhs and rhs cannot be compared")

        # equality test expressions are always boolean results
        self.type = ctx.global_env.lookup_type(6, self.position, 'boolean')


# Arithmetic operations

@dataclass
class PlusNode(BinaryArithNode):
    """An AST node representing a binary plus operation."""

    op_name: str = '+'

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        # must be primitive
        if not (isinstance(self.lhs.type, uctypes.PrimitiveType)
                and isinstance(self.rhs.type, uctypes.PrimitiveType)):
            error(6, self.position,
                  "lhs and rhs operands must be primitive types")

        # cannot be null or void
        elif self.lhs.type.name == 'void' or self.lhs.type.name == 'null':
            error(6, self.position,
                  "lhs operant cannot be of type void or null")
        elif self.rhs.type.name == 'void' or self.rhs.type.name == 'null':
            error(6, self.position,
                  "rhs operant cannot be of type void or null")

        # if one is boolean other must be strings
        elif self.lhs.type.name == 'boolean'\
                and self.rhs.type.name != 'string':
            error(6, self.position,
                  "lhs operand is of type boolean, "
                  + "so rhs type must be of type string")
        elif self.rhs.type.name == 'boolean'\
                and self.lhs.type.name != 'string':
            error(6, self.position,
                  "rhs operand is of type boolean, "
                  + "so lhs type must be of type string")

        # if one or both is string, resulting type is string
        elif self.lhs.type.name == 'string' or self.rhs.type.name == 'string':
            self.type = ctx.global_env.lookup_type(6, self.position, 'string')

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("uc_add(", end="")
        self.lhs.gen_function_defs(ctx)
        ctx.print(", ", end="")
        self.rhs.gen_function_defs(ctx)
        ctx.print(")", end="")


@ dataclass
class MinusNode(BinaryArithNode):
    """An AST node representing a binary minus operation."""

    op_name: str = '-'

    # add your code below if necessary


@ dataclass
class TimesNode(BinaryArithNode):
    """An AST node representing a binary times operation."""

    op_name: str = '*'

    # add your code below if necessary


@ dataclass
class DivideNode(BinaryArithNode):
    """An AST node representing a binary divide operation."""

    op_name: str = '/'

    # add your code below if necessary


@ dataclass
class ModuloNode(BinaryArithNode):
    """An AST node representing a binary modulo operation."""

    op_name: str = '%'

    # add your code below if necessary
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not (uctypes.is_integral_type(self.lhs.type)
                and uctypes.is_integral_type(self.rhs.type)):
            error(6, self.position,
                  "lhs and rhs must be of type int or long")


# Logical operations

@ dataclass
class LogicalOrNode(BinaryLogicNode):
    """An AST node representing a logical or operation."""

    op_name: str = '||'

    # add your code below if necessary


@ dataclass
class LogicalAndNode(BinaryLogicNode):
    """An AST node representing a logical and operation."""

    op_name: str = '&&'

    # add your code below if necessary


# Arithmetic comparisons

@ dataclass
class LessNode(BinaryCompNode):
    """An AST node representing a less than operation."""

    op_name: str = '<'

    # add your code below if necessary


@ dataclass
class LessEqualNode(BinaryCompNode):
    """An AST node representing a less than or equal operation.

    lhs is the left-hand operand and rhs is the right-hand operand.
    """

    op_name: str = '<='

    # add your code below if necessary


@ dataclass
class GreaterNode(BinaryCompNode):
    """An AST node representing a greater than operation."""

    op_name: str = '>'

    # add your code below if necessary


@ dataclass
class GreaterEqualNode(BinaryCompNode):
    """An AST node representing a greater than or equal operation."""

    op_name: str = '>='

    # add your code below if necessary


# Equality comparisons

@ dataclass
class EqualNode(EqualityTestNode):
    """An AST node representing an equality comparison."""

    op_name: str = '=='

    # add your code below if necessary


@ dataclass
class NotEqualNode(EqualityTestNode):
    """An AST node representing an inequality comparison."""

    op_name: str = '!='

    # add your code below if necessary


# Other binary operations

@ dataclass
class AssignNode(BinaryOpNode):
    """An AST node representing an assignment operation."""

    op_name: str = '='

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not uctypes.is_compatible(self.rhs.type, self.lhs.type):
            error(6, self.position,
                  "rhs operand must be "
                  + "implicitly convertible to lhs operand")
        elif not self.lhs.is_lvalue():
            error(6, self.position, "lhs operand must produce l-value")
        else:
            self.type = self.lhs.type

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        self.lhs.gen_function_defs(ctx)
        ctx.print(" = ", end="")
        self.rhs.gen_function_defs(ctx)


@ dataclass
class PushNode(BinaryOpNode):
    """An AST node representing an array insertion operation."""

    op_name: str = '<<'

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not isinstance(self.lhs.type, uctypes.ArrayType):
            error(6, self.position, "lhs operand must be of ArrayType")
        elif not uctypes.is_compatible(self.rhs.type, self.lhs.type.elem_type):
            error(6, self.position,
                  "rhs operand is not "
                  + "implicitly convertible to lhs operand")
        else:
            self.type = self.lhs.type

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("uc_array_push(", end="")
        self.lhs.gen_function_defs(ctx)
        ctx.print(", ", end="")
        self.rhs.gen_function_defs(ctx)
        ctx.print(")", end="")


@ dataclass
class PopNode(BinaryOpNode):
    """An AST node representing an array extraction operation."""

    op_name: str = '>>'

    # add your code below
    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        super().type_check(ctx)
        if not isinstance(self.lhs.type, uctypes.ArrayType):
            error(6, self.position, "lhs operand must be of ArrayType")
        elif not (self.rhs.type.name == 'null' or self.rhs.is_lvalue()):
            error(6, self.position,
                  "rhs operand must be null or lvalue")
        elif self.rhs.is_lvalue() and \
                (not uctypes.is_compatible(self.lhs.type.elem_type,
                                           self.rhs.type)):
            error(6, self.position,
                  "rhs operand is l-value, so "
                  + "elemtype of lhs operand must be "
                  + "implicitly convertible")
        else:
            self.type = self.lhs.type

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ctx.print("uc_array_pop(", end="")
        self.lhs.gen_function_defs(ctx)
        ctx.print(", ", end="")
        self.rhs.gen_function_defs(ctx)
        ctx.print(")", end="")
