#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "use_before_decl.cpp"

  void UC_CONCAT(UC_TYPEDEF(baz), _test)(UC_REFERENCE(baz));
  void UC_CONCAT(UC_TYPEDEF(foo), _test)(UC_REFERENCE(foo));

}

int main() {
  return 0;
}
