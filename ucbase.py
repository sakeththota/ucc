"""
ucbase.py.

This file contains definitions of the base AST node, declaration
nodes, global and local environments, and utility functions.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

import dataclasses
from dataclasses import dataclass
import itertools
import sys
from typing import List, Optional, ClassVar, Iterator
from ucerror import error
import uctypes
import ucfunctions


#################
# AST Functions #
#################

def attribute():
    """Specify that a field is an attribute.

    An attribute is initially defaulted to None but will be filled in
    with its proper value in an analysis phase.
    """
    return dataclasses.field(default=None, init=False)


def ast_map(func, item, terminal_func=None):
    """Map the given function on an AST item.

    If the item is a list, then the function is mapped across its
    elements. If the item is a terminal rather than an AST node, then
    terminal_func is applied if given.
    """
    if isinstance(item, list):
        for i in item:
            ast_map(func, i, terminal_func)
    elif isinstance(item, ASTNode):
        func(item)
    elif terminal_func:
        terminal_func(item)


################################
# Environments in the Compiler #
################################

class GlobalEnv:
    """A class that represents the global environment of a uC program.

    Maps names to types and to functions.
    """

    def __init__(self):
        """Initialize the environment with built-in names."""
        self.types = {}
        self.functions = {}
        uctypes.add_builtin_types(self.types)
        ucfunctions.add_builtin_functions(self.functions, self.types)

    def add_type(self, phase, position, name, declnode):
        """Add the given type to this environment.

        phase is the current compiler phase, position is the source
        position of the type declaration, name is a string containing
        the name of the type, and declnode is the AST node
        corresponding to the declaration. Reports an error if a type
        of the given name is already defined.
        """
        if name in self.types:
            error(phase, position, 'redefinition of type ' + name)
        else:
            self.types[name] = uctypes.UserType(name, declnode)
        return self.types[name]

    def add_function(self, phase, position, name, declnode):
        """Add the given function to this environment.

        phase is the current compiler phase, position is the source
        position of the function declaration, name is a string
        containing the name of the function, and declnode is the AST
        node corresponding to the declaration. Reports an error if a
        function of the given name is already defined.
        """
        if name in self.functions:
            error(phase, position, 'redefinition of function ' + name)
        else:
            self.functions[name] = ucfunctions.UserFunction(name,
                                                            declnode)
        return self.functions[name]

    def lookup_type(self, phase, position, name, strict=True):
        """Return the type represented by the given name.

        phase is the current compiler phase, position is the source
        position that resulted in this lookup, name is a string
        containing the name of the type to look up. If strict is True,
        then an error is reported if the name is not found, and the
        int type is returned. Otherwise, if the name is not found,
        None is returned.
        """
        if name not in self.types:
            if strict:
                error(phase, position, 'undefined type ' + name)
                return self.types['int']  # treat it as int by default
            return None
        return self.types[name]

    def lookup_function(self, phase, position, name, strict=True):
        """Return the function represented by the given name.

        phase is the current compiler phase, position is the source
        position that resulted in this lookup, name is a string
        containing the name of the function to look up. If strict is
        True, then an error is reported if the name is not found, and
        string_to_int function is returned. Otherwise, if the name is
        not found, None is returned.
        """
        if name not in self.functions:
            if strict:
                error(phase, position, 'undefined function ' + name)
                return self.functions['string_to_int']  # default
            return None
        return self.functions[name]

    def get_type_names(self):
        """Return a sequence of the type names in the environment."""
        return self.types.keys()

    def get_function_names(self):
        """Return a sequence of the function names in the environment."""
        return self.functions.keys()


class VarEnv:
    """A class that represents a local environment in a uC program.

    Maps names to types of fields, parameters, and variables.
    """

    def __init__(self, global_env):
        """Initialize this to an empty local environment.

        The given global environment is used to lookup a default type
        when a name is not defined.
        """
        self.global_env = global_env
        self.var_types = {}

    def add_variable(self, phase, position, name, var_type, kind_str):
        """Insert a variable into this environment.

        phase is the current compiler phase, position is the source
        position of the field, parameter, or variable declaration,
        name is a string containing the name of the field, variable,
        or parameter, var_type is its type, and kind_str is one of
        'field, 'variable', or 'parameter'. Reports an error if a
        field, variable, or parameter of the given name already exists
        in this environment.
        """
        if name in self.var_types:
            error(phase, position,
                  'redeclaration of {0} {1}'.format(kind_str, name))
        else:
            self.var_types[name] = var_type

    def contains(self, name):
        """Return whether or not name is defined in the environment."""
        return name in self.var_types

    def get_type(self, phase, position, name):
        """Look up a name and return the type of the entity it names.

        phase is the current compiler phase, position is the source
        position where the name appears, and name is a string
        containing the name. Reports an error if the given name is not
        defined and returns the int type.
        """
        if name not in self.var_types:
            error(phase, position, 'undefined variable ' + name)
            # default to int
            return self.global_env.lookup_type(phase, position, 'int')
        return self.var_types[name]


#################
# Base AST Node #
#################

@dataclass
class ASTNode:
    """The base class for all AST nodes.

    Implements default functionality for an AST node.
    """

    # used for giving each node a unique id
    next_id: ClassVar[Iterator[int]] = itertools.count()

    node_id: int = dataclasses.field(
        init=False, default_factory=lambda: next(ASTNode.next_id)
    )
    position: int

    @property
    def children(self):
        """Return the children of this AST node."""
        return [self.__getattribute__(field)
                for field in self.child_names]

    @property
    def child_names(self):
        """Return the names of the children of this AST node."""
        return [field.name for field in dataclasses.fields(self)[2:]
                if field.default == dataclasses.MISSING]

    def __str__(self):
        """Return a string representation of this and its children."""
        result = '{' + type(self).__name__ + ':'
        for name in self.child_names:
            result += ' ' + child_str(self.__dict__[name])
        return result + '}'

    def find_decls(self, ctx):
        """Process the type and function declarations in this subtree.

        Adds the types and functions that are found to ctx.global_env.
        Reports an error if a type or function is multiply defined.
        """
        ast_map(lambda n: n.find_decls(ctx), self.children)

    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        ast_map(lambda n: n.resolve_types(ctx), self.children)

    def resolve_calls(self, ctx):
        """Match function calls to the actual functions they name.

        Uses ctx.global_env to look up a function name. Reports an
        error if an unknown function is named.
        """
        ast_map(lambda n: n.resolve_calls(ctx), self.children)

    def check_names(self, ctx):
        """Check names in types and functions for uniqueness.

        Checks the names introduced within a type or function to
        ensure they are unique in the scope of the type or
        function.
        """
        ast_map(lambda n: n.check_names(ctx), self.children)

    def basic_control(self, ctx):
        """Check basic control flow within this AST node."""
        ast_map(lambda n: n.basic_control(ctx), self.children)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        ast_map(lambda n: n.type_check(ctx), self.children)

    def advanced_control(self, ctx):
        """Check advanced control flow within this AST node."""
        ast_map(lambda n: n.advanced_control(ctx), self.children)

    def write_types(self, ctx):
        """Write out a representation of this AST to ctx.out.

        Includes type annotations for each node that has a type.
        """
        ctx.print(type(self).__name__, indent=True, end='')
        if 'type' in dir(self):
            node_type = self.__getattribute__('type')
            ctx.print(': {0}'.format(node_type.name if
                                     node_type else node_type),
                      end='')
        ctx.print(' {')
        new_ctx = ctx.clone()
        new_ctx.indent += '  '
        ast_map(lambda n: n.write_types(new_ctx), self.children,
                lambda s: new_ctx.print(s, indent=True))
        ctx.print('}', indent=True)

    def gen_type_decls(self, ctx):
        """Generate type decls."""
        ast_map(lambda n: n.gen_type_decls(ctx), self.children)

    def gen_function_decls(self, ctx):
        """Generate function decls."""
        ast_map(lambda n: n.gen_function_decls(ctx), self.children)

    def gen_type_defs(self, ctx):
        """Generate type defs."""
        ast_map(lambda n: n.gen_type_defs(ctx), self.children)

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        ast_map(lambda n: n.gen_function_defs(ctx), self.children)

##############
# Start Node #
##############


@dataclass
class DeclNode(ASTNode):
    """The base node for type and function declarations."""


@dataclass
class ProgramNode(ASTNode):
    """Represents a uC program."""

    decls: List[DeclNode]


##########################
# Names and Declarations #
##########################

@dataclass
class NameNode(ASTNode):
    """An AST node representing a name.

    raw is the actual string containing the name.
    """

    raw: str

    # add your code below if necessary


@dataclass
class BaseTypeNameNode(ASTNode):
    """The base node for type names and array type names.

    type is the instance of uctypes.Type associated with the type
    named by this node.
    """

    type: Optional[uctypes.Type] = attribute()


@dataclass
class TypeNameNode(BaseTypeNameNode):
    """An AST node representing the name of a type.

    name is a node representing the name of the type.
    """

    name: NameNode

    # add your code below if necessary
    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        if self.name.raw == 'void' and not ctx['is_return']:
            error(2, self.position, "void can only be used as return type")
        self.type = ctx.global_env.lookup_type(
            2, self.position, self.name.raw)


@dataclass
class ArrayTypeNameNode(BaseTypeNameNode):
    """An AST node representing an array type.

    elem_type is a node representing the element type.
    """

    elem_type: BaseTypeNameNode

    # add your code below if necessary
    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        super().resolve_types(ctx)
        self.type = self.elem_type.type.array_type


@dataclass
class VarDeclNode(ASTNode):
    """An AST node representing a variable or field declaration.

    vartype is a node representing the type and name is a node
    representing the name.
    """

    vartype: BaseTypeNameNode
    name: NameNode

    # add your code below if necessary


@dataclass
class ParameterNode(ASTNode):
    """An AST node representing a parameter declaration.

    vartype is a node representing the type and name is a node
    representing the name.
    """

    vartype: BaseTypeNameNode
    name: NameNode

    # add your code below if necessary


@dataclass
class StructDeclNode(DeclNode):
    """An AST node representing a type declaration.

    name is the name of the type and vardecls is a list of field
    declarations. type is the instance of uctypes.Type that is
    associated with this declaration.
    """

    name: NameNode
    vardecls: List[VarDeclNode]
    type: Optional[uctypes.Type] = attribute()
    localenv: Optional[VarEnv] = attribute()

    # add your code below
    def find_decls(self, ctx):
        """Process the type and function declarations in this subtree.

        Adds the types and functions that are found to ctx.global_env.
        Reports an error if a type or function is multiply defined.
        """
        ctx.global_env.add_type(1, self.position, self.name.raw, self)
        self.type = ctx.global_env.lookup_type(
            1, self.position, self.name.raw)
        super().find_decls(ctx)

    def check_names(self, ctx):
        """Check names in types and functions for uniqueness.

        Checks the names introduced within a type or function to
        ensure they are unique in the scope of the type or
        function.
        """
        self.localenv = VarEnv(ctx.global_env)
        for var in self.vardecls:
            self.localenv.add_variable(
                4, self.position, var.name.raw, var.vartype.type, 'field')
        super().check_names(ctx)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        new_ctx = ctx.clone()
        new_ctx['local_env'] = self.localenv
        super().type_check(new_ctx)

    def gen_type_decls(self, ctx):
        """Generate type decls."""
        ctx.print(f"struct UC_TYPEDEF({self.name.raw});", indent=True)

    def gen_type_defs(self, ctx):
        """Generate type defs."""
        # name
        ctx.print(f"struct UC_TYPEDEF({self.name.raw})", indent=True, end="")
        ctx.print(" {")

        # variable declarations
        ctx.indent += "  "
        for var in self.vardecls:
            ctx.print(
                f"{var.vartype.type.mangle()} "
                + f"UC_VAR({var.name.raw});", indent=True)

        # defualt constructor
        ctx.print(f"UC_TYPEDEF({self.name.raw})() = default;", indent=True)

        # parameterized constructor
        if len(self.vardecls) != 0:
            ctx.print(f"UC_TYPEDEF({self.name.raw})", indent=True, end="")
            ctx.print("(", end="")
            for i, var in enumerate(self.vardecls):
                ctx.print(
                    f"const {var.vartype.type.mangle()} &var{i}", end="")
                if i != len(self.vardecls)-1:
                    ctx.print(", ", end="")
            ctx.print(") {")
            ctx.indent += "  "
            for i, var in enumerate(self.vardecls):
                ctx.print(f"UC_VAR({var.name.raw}) = var{i};", indent=True)
            ctx.indent = "    "
            ctx.print("}", indent=True)

        # overloaded == operator
        ctx.print(
            "UC_PRIMITIVE(boolean) operator=="
            + f"(const UC_TYPEDEF({self.name.raw}) &rhs)"
            + " const", indent=True, end="")
        ctx.print(" {")
        ctx.indent += "  "
        ctx.print("return ", indent=True, end="")
        if len(self.vardecls) == 0:
            ctx.print("true", end="")
        for i, var in enumerate(self.vardecls):
            ctx.print(
                f"UC_VAR({var.name.raw})"
                + f" == rhs.UC_VAR({var.name.raw})", end="")
            if i != len(self.vardecls)-1:
                ctx.print(" && ", end="")
        ctx.print(";")
        ctx.indent = "    "
        ctx.print("}", indent=True)

        # overloaded != operator
        ctx.print(
            "UC_PRIMITIVE(boolean) operator!="
            + f"(const UC_TYPEDEF({self.name.raw}) "
            + "&rhs) const", indent=True, end="")
        ctx.print(" {")
        ctx.indent += "  "
        ctx.print("return !((*this)==rhs);", indent=True)
        ctx.indent = "    "
        ctx.print("}", indent=True)
        ctx.indent = "  "
        ctx.print("};\n", indent=True)


@ dataclass
class FunctionDeclNode(DeclNode):
    """An AST node representing a function declaration.

    rettype is a node representing the return type, name is the name
    of the function, parameters is a list of parameter declarations,
    vardecls is a list of local variable declarations, and body is the
    body of the function.
    """

    rettype: BaseTypeNameNode
    name: NameNode
    parameters: List[ParameterNode]
    vardecls: List[VarDeclNode]
    body: 'BlockNode'  # put type in string since it hasn't been defined yet
    func: Optional[ucfunctions.Function] = attribute()
    localenv: Optional[VarEnv] = attribute()

    # add your code below
    def find_decls(self, ctx):
        """Process the type and function declarations in this subtree.

        Adds the types and functions that are found to ctx.global_env.
        Reports an error if a type or function is multiply defined.
        """
        ctx.global_env.add_function(1, self.position, self.name.raw, self)
        self.func = ctx.global_env.lookup_function(
            1, self.position, self.name.raw)
        super().find_decls(ctx)

    def resolve_types(self, ctx):
        """Resolve type names to the actual types they name.

        Uses ctx.global_env to look up a type name. Reports
        an error if an unknown type is named.
        """
        new_ctx = ctx.clone()
        new_ctx['is_return'] = True
        self.rettype.resolve_types(new_ctx)
        self.func.rettype = self.rettype.type
        for param in self.parameters:
            param.resolve_types(ctx)
            self.func.add_param_types([param.vartype.type])
        for var in self.vardecls:
            var.resolve_types(ctx)
        self.body.resolve_types(ctx)

    def check_names(self, ctx):
        """Check names in types and functions for uniqueness.

        Checks the names introduced within a type or function to
        ensure they are unique in the scope of the type or
        function.
        """
        self.localenv = VarEnv(ctx.global_env)
        for param in self.parameters:
            self.localenv.add_variable(
                4, self.position, param.name.raw,
                param.vartype.type, 'parameter')
        for var in self.vardecls:
            self.localenv.add_variable(
                4, self.position, var.name.raw, var.vartype.type, 'variable')
        super().check_names(ctx)

    def type_check(self, ctx):
        """Compute the type of each expression.

        Uses ctx['local_env'] to compute the type of a local name.
        Checks that the type of an expression is compatible with the
        context in which it is used.
        """
        new_ctx = ctx.clone()
        new_ctx['local_env'] = self.localenv
        new_ctx['rettype'] = self.func.rettype
        super().type_check(new_ctx)

    def gen_function_decls(self, ctx):
        """Generate function decls."""
        # return type
        ctx.print(self.func.rettype.mangle(), indent=True)

        # function name
        new_ctx = ctx.clone()
        new_ctx.indent += "  "
        new_ctx.print(self.func.mangle(), indent=True, end="")

        # function parameters
        ctx.print("(", end="")
        for i, param in enumerate(self.parameters):
            ctx.print(
                f"{param.vartype.type.mangle()}"
                + f" UC_VAR({param.name.raw})", end="")
            if i != len(self.parameters)-1:
                ctx.print(",", end="")
        ctx.print(");")

    def gen_function_defs(self, ctx):
        """Generate function defs."""
        # return type
        ctx.print(self.func.rettype.mangle(), indent=True)

        # function name
        ctx.indent += "  "
        ctx.print(self.func.mangle(), indent=True, end="")

        # function parameters
        ctx.print("(", end="")
        for i, param in enumerate(self.parameters):
            ctx.print(
                f"{param.vartype.type.mangle()}"
                + f" UC_VAR({param.name.raw})", end="")
            if i != len(self.parameters)-1:
                ctx.print(",", end="")
        ctx.print(") {")

        # local variable declarations
        ctx.indent += "  "
        for var in self.vardecls:
            ctx.print(
                f"{var.vartype.type.mangle()}"
                + f" UC_VAR({var.name.raw});", indent=True)

        super().gen_function_defs(ctx)

        ctx.indent = "  "
        ctx.print("}", indent=True)


######################
# Printing Functions #
######################

def child_str(child):
    """Convert an AST item into a string.

    Converts list elements to strings using str() rather than repr().
    """
    if isinstance(child, list):
        result = '['
        if child:
            result += child_str(child[0])
        for i in range(1, len(child)):
            result += ', ' + child_str(child[i])
        return result + ']'
    return str(child)


def graph_gen(item, parent_id=None, child_num=None, child_name=None,
              out=sys.stdout):
    """Print a graph representation of the given AST node to out.

    The output is in a format compatible with Graphviz.
    """
    if isinstance(item, ASTNode):
        if parent_id:
            edge = '  {0} -> {{N{1} [label="{2}{4}"]}} [label="{3}"]'
            print(edge.format(parent_id, item.node_id,
                              type(item).__name__, child_name,
                              ' ({})'.format(item.type.name)
                              if 'type' in item.__dict__ and item.type
                              else ''),
                  file=out)
            new_parent_id = 'N{0}'.format(item.node_id)
        else:
            print('digraph {', file=out)
            new_parent_id = type(item).__name__
        for i, child in enumerate(item.children):
            graph_gen(child, new_parent_id, i, item.child_names[i],
                      out)
        if not parent_id:
            print('}', file=out)
    elif isinstance(item, list):
        edge = '  {0} -> {{{0}L{1} [label="[list]"]}} [label="{2}"]'
        print(edge.format(parent_id, child_num, child_name), file=out)
        for i, child in enumerate(item):
            graph_gen(child, '{0}L{1}'.format(parent_id, child_num),
                      i, i, out)
    else:
        edge = '  {0} -> {{{0}T{1} [label="{2}"]}} [label="{3}"]'
        print(edge.format(parent_id, child_num,
                          str(item).replace('\\', '\\\\').replace('"', '\\"'),
                          child_name),
              file=out)
