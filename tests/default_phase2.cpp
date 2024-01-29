#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "default.cpp"

  void test() {
    UC_FUNCTION(main)(UC_ARRAY(UC_PRIMITIVE(string)){});
  }

}

int main() {
  uc::test();
  return 0;
}
