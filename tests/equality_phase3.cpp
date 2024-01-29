#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "equality.cpp"

  void test_default() {
    UC_REFERENCE(bar) var0 = uc_make_object<UC_REFERENCE(bar)>();
    UC_REFERENCE(bar) var0b = uc_make_object<UC_REFERENCE(bar)>();
    assert(var0 == var0b);
    assert(!(var0 != var0b));
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>();
    UC_REFERENCE(foo) var1b = uc_make_object<UC_REFERENCE(foo)>();
    assert(var1 == var1b);
    assert(!(var1 != var1b));
    assert(var1->UC_VAR(x) == UC_PRIMITIVE(int){});
  }

  void test_non_default_with_defaults() {
    UC_REFERENCE(bar) var0 = uc_make_object<UC_REFERENCE(bar)>();
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>(UC_PRIMITIVE(int){});
    assert(var1->UC_VAR(x) == UC_PRIMITIVE(int){});
  }

  void test_non_default_with_non_defaults() {
    UC_REFERENCE(bar) var0 = uc_make_object<UC_REFERENCE(bar)>();
    UC_REFERENCE(bar) var0b = uc_make_object<UC_REFERENCE(bar)>();
    UC_REFERENCE(bar) var0c = uc_make_object<UC_REFERENCE(bar)>();
    assert(var0 == var0b);
    assert(!(var0 != var0b));
    UC_PRIMITIVE(int) arg1_0 = 1;
    UC_PRIMITIVE(int) arg1_0c = 2;
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>(arg1_0);
    UC_REFERENCE(foo) var1b = uc_make_object<UC_REFERENCE(foo)>(arg1_0);
    UC_REFERENCE(foo) var1c = uc_make_object<UC_REFERENCE(foo)>(arg1_0c);
    assert(var1 == var1b);
    assert(!(var1 != var1b));
    assert(var1 != var1c);
    assert(!(var1 == var1c));
    assert(var1->UC_VAR(x) == arg1_0);
  }

}

int main() {
  uc::test_default();
  uc::test_non_default_with_defaults();
  uc::test_non_default_with_non_defaults();
  return 0;
}
