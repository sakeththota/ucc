#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "literals.cpp"

  void test_default() {
  }

  void test_non_default_with_defaults() {
  }

  void test_non_default_with_non_defaults() {
  }

}

int main() {
  uc::test_default();
  uc::test_non_default_with_defaults();
  uc::test_non_default_with_non_defaults();
  return 0;
}
