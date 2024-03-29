#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "use_before_decl.cpp"

  void test_default() {
    UC_REFERENCE(baz) var0 = uc_make_object<UC_REFERENCE(baz)>();
    UC_REFERENCE(baz) var0b = uc_make_object<UC_REFERENCE(baz)>();
    assert(var0 == var0b);
    assert(!(var0 != var0b));
    assert(var0->UC_VAR(s) == UC_PRIMITIVE(string){});
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>();
    UC_REFERENCE(foo) var1b = uc_make_object<UC_REFERENCE(foo)>();
    assert(var1 == var1b);
    assert(!(var1 != var1b));
    assert(var1->UC_VAR(b) == UC_REFERENCE(baz){});
  }

  void test_non_default_with_defaults() {
    UC_REFERENCE(baz) var0 = uc_make_object<UC_REFERENCE(baz)>(UC_PRIMITIVE(string){});
    assert(var0->UC_VAR(s) == UC_PRIMITIVE(string){});
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>(UC_REFERENCE(baz){});
    assert(var1->UC_VAR(b) == UC_REFERENCE(baz){});
  }

  void test_non_default_with_non_defaults() {
    UC_PRIMITIVE(string) arg0_0 = "foo1";
    UC_PRIMITIVE(string) arg0_0c = "foo2";
    UC_REFERENCE(baz) var0 = uc_make_object<UC_REFERENCE(baz)>(arg0_0);
    UC_REFERENCE(baz) var0b = uc_make_object<UC_REFERENCE(baz)>(arg0_0);
    UC_REFERENCE(baz) var0c = uc_make_object<UC_REFERENCE(baz)>(arg0_0c);
    assert(var0 == var0b);
    assert(!(var0 != var0b));
    assert(var0 != var0c);
    assert(!(var0 == var0c));
    assert(var0->UC_VAR(s) == arg0_0);
    UC_REFERENCE(baz) arg1_0 = uc_make_object<UC_REFERENCE(baz)>();
    UC_REFERENCE(baz) arg1_0c = uc_make_object<UC_REFERENCE(baz)>();
    UC_REFERENCE(foo) var1 = uc_make_object<UC_REFERENCE(foo)>(arg1_0);
    UC_REFERENCE(foo) var1b = uc_make_object<UC_REFERENCE(foo)>(arg1_0);
    UC_REFERENCE(foo) var1c = uc_make_object<UC_REFERENCE(foo)>(arg1_0c);
    assert(var1 == var1b);
    assert(!(var1 != var1b));
    assert(var1->UC_VAR(b) == arg1_0);
  }

}

int main() {
  uc::test_default();
  uc::test_non_default_with_defaults();
  uc::test_non_default_with_non_defaults();
  return 0;
}
