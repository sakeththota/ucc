#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "length_field.cpp"

  void UC_CONCAT(UC_TYPEDEF(foo), _test)(UC_REFERENCE(foo));

}

int main() {
  return 0;
}
