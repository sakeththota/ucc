#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "length_field.cpp"

  void test() {
    UC_FUNCTION(bar)(UC_REFERENCE(foo){});
    UC_FUNCTION(main)(UC_ARRAY(UC_PRIMITIVE(string)){});
  }

}

int main() {
  uc::test();
  return 0;
}
