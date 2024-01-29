"""
ucbackend.py.

This file implements entry points into the backend of the compiler.

Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
"""

# NOTE: This file is for the backend project. Ignore it for the
#       frontend.

import uccontext


###################
# Code Generation #
###################

def gen_header(_, global_env, out):
    """Generate the header for a uC program, writing it to out.

    The header includes library code written in C++ and opens the uc
    namespace.
    """
    ctx = uccontext.PhaseContext(0, global_env, out, '  ')
    ctx.print('#include "defs.h"')
    ctx.print('#include "ref.h"')
    ctx.print('#include "array.h"')
    ctx.print('#include "library.h"')
    ctx.print('#include "expr.h"')
    ctx.print()
    ctx.print('namespace uc {\n')
    ctx.indent = "  "


def gen_footer(_, global_env, out):
    """Generate the footer for a uC program, writing it to out.

    The footer closes the uc namespace and bootstraps execution of a
    uC program.
    """
    ctx = uccontext.PhaseContext(0, global_env, out, '  ')
    ctx.print('} // namespace uc\n')
    ctx.print('int main(int argc, char **argv) {')
    ctx.print('  uc::UC_ARRAY(uc::UC_PRIMITIVE(string)) args = ' +
              'uc::uc_make_array_of<uc::UC_PRIMITIVE(string)>();')
    ctx.print('  for (int i = 1; i < argc; i++) {')
    ctx.print('    uc::uc_array_push(args, ' +
              'uc::UC_PRIMITIVE(string)(argv[i]));')
    ctx.print('  }')
    ctx.print('  uc::UC_FUNCTION(main)(args);')
    ctx.print('  return 0;')
    ctx.print('}')


def gen_type_decls(tree, global_env, out):
    """Generate forward type declarations, writing them to out."""
    ctx = uccontext.PhaseContext(1, global_env, out, '  ')
    ctx.print('// Forward type declarations\n', indent=True)
    # add your code here
    tree.gen_type_decls(ctx)
    ctx.print()


def gen_function_decls(tree, global_env, out):
    """Generate forward function declarations, writing them to out."""
    ctx = uccontext.PhaseContext(2, global_env, out, '  ')
    ctx.print('// Forward function declarations\n', indent=True)
    # add your code here
    tree.gen_function_decls(ctx)
    ctx.print()


def gen_type_defs(tree, global_env, out):
    """Generate full type definitions, writing them to out."""
    ctx = uccontext.PhaseContext(3, global_env, out, '  ')
    ctx.print('// Full type definitions\n', indent=True)
    # add your code here
    tree.gen_type_defs(ctx)


def gen_function_defs(tree, global_env, out):
    """Generate full function definitions, writing them to out."""
    ctx = uccontext.PhaseContext(4, global_env, out, '  ')
    ctx.print('// Full function definitions\n', indent=True)
    # add your code here
    ctx['nested'] = False
    tree.gen_function_defs(ctx)
