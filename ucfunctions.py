"""
ucfunctions.py.

This file contains definitions of classes that represent uC functions,
as well as utility functions that operate on functions.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

from ucerror import error
import uctypes


class Function:
    """A class that represents a uC function."""

    def __init__(self, name):
        """Initialize this function with the given name.

        The return is initially set to None, and the parameters to an
        empty set.
        """
        self.name = name
        self.rettype = None
        self.param_types = []

    def __str__(self):
        """Return the name of this function."""
        return self.name

    def mangle(self):
        """Return the mangled name of this function.

        The mangled name is the name that should be used in code
        generation.
        """
        return 'UC_FUNCTION({0})'.format(self.name)

    def check_args(self, phase, position, args):
        """Check if the arguments are compatible with this function.

        The given arguments are compared with the parameter types of
        this function. The arguments must have already have their
        types computed. phase is the current compiler phase, position
        is the source position where this check occurs. Reports an
        error if the arguments are incompatible with this function.
        """
        if len(args) != len(self.param_types):
            error(phase, position,
                  f"function {self.name}" +
                  f"expected {len(self.param_types)} argument(s),"
                  + f"but got {len(args)}")
        else:
            for arg, param in zip(args, self.param_types):
                if not uctypes.is_compatible(arg.type, param):
                    error(phase, position,
                          f"type {arg.type} of "
                          + "argument is not compatible with parameter "
                          + f"of type {param}")


class PrimitiveFunction(Function):
    """A class that represents a primitive uC function."""

    def __init__(self, name, rettype, param_types, type_env):
        """Initialize this function with the given name.

        rettype is the name of the return type, param_types is a
        sequence of names of the parameter types, and type_env is the
        dictionary in which to look up type names.
        """
        super().__init__(name)
        self.rettype = type_env[rettype]
        for param in param_types:
            self.param_types.append(type_env[param])


class UserFunction(Function):
    """A class that represents a user-defined uC function."""

    def __init__(self, name, decl):
        """Initialize this function with the given name.

        The return type is initially set to None, and the parameter
        types to an empty set. decl is the AST node that defines this
        function.
        """
        super().__init__(name)
        self.decl = decl

    def add_param_types(self, param_types):
        """Add parameter types to this parameter list of this function.

        param_types must be a sequence of items, each of which must be
        of type uctypes.Type.
        """
        self.param_types += param_types


def make_conversion(target, source, type_env):
    """Create a primitive conversion function.

    The resulting function converts the type named by source to that
    named by target. type_env is the dictionary in which to look up
    type names.
    """
    return PrimitiveFunction('{0}_to_{1}'.format(source, target),
                             target, (source,), type_env)


def add_conversions(func_env, type_env):
    """Create all the primitive conversion functions.

    func_env is the dictionary in which to insert the conversion
    functions. type_env is the dictionary to use to look up type
    names.
    """
    types = ('int', 'long', 'float', 'string')
    for type1 in types:
        for type2 in types:
            if type1 != type2:
                func = make_conversion(type1, type2, type_env)
                func_env[func.name] = func
    func = make_conversion('boolean', 'string', type_env)
    func_env[func.name] = func
    func = make_conversion('string', 'boolean', type_env)
    func_env[func.name] = func


def add_builtin_functions(func_env, type_env):
    """Create all the primitive uC functions.

    func_env is the dictionary in which to insert the conversion
    functions. type_env is the dictionary to use to look up type
    names.
    """
    add_conversions(func_env, type_env)
    # string functions
    func_env['length'] = PrimitiveFunction('length', 'int',
                                           ('string',), type_env)
    func_env['substr'] = PrimitiveFunction('substr', 'string',
                                           ('string', 'int', 'int'),
                                           type_env)
    func_env['ordinal'] = PrimitiveFunction('ordinal', 'int',
                                            ('string',), type_env)
    func_env['character'] = PrimitiveFunction('character', 'string',
                                              ('int',), type_env)

    # numerical functions
    func_env['pow'] = PrimitiveFunction('pow', 'float',
                                        ('float', 'float'),
                                        type_env)
    func_env['sqrt'] = PrimitiveFunction('sqrt', 'float',
                                         ('float',), type_env)
    func_env['ceil'] = PrimitiveFunction('ceil', 'float',
                                         ('float',), type_env)
    func_env['floor'] = PrimitiveFunction('floor', 'float',
                                          ('float',), type_env)

    # print functions
    func_env['print'] = PrimitiveFunction('print', 'void',
                                          ('string',), type_env)
    func_env['println'] = PrimitiveFunction('println', 'void',
                                            ('string',), type_env)

    # input functions
    func_env['peekchar'] = PrimitiveFunction('peekchar', 'string', (),
                                             type_env)
    func_env['readchar'] = PrimitiveFunction('readchar', 'string', (),
                                             type_env)
    func_env['readline'] = PrimitiveFunction('readline', 'string', (),
                                             type_env)
