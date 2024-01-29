#include <cassert>
#include "defs.h"
#include "ref.h"
#include "array.h"
#include "library.h"
#include "expr.h"

namespace uc {

  #include "particle.cpp"

  void UC_CONCAT(UC_TYPEDEF(particle), _test)(UC_REFERENCE(particle));

}

int main() {
  return 0;
}
