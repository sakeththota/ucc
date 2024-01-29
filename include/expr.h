#pragma once

/**
 * expr.h
 *
 * This file includes function template overloads for polymorphic
 * operations, specifically obtaining the id of an object, accessing
 * the length field of an object, and adding two values together.
 *
 * Project UID c49e54971d13f14fbc634d7a0fe4b38d421279e7
 */

#include "array.h"

namespace uc {

// Template for obtaining the id of an object.
template <class T>
UC_PRIMITIVE(long)
uc_id(T ref) {
  auto ptr_val = reinterpret_cast<std::uintptr_t>(ref.get());
  return static_cast<UC_PRIMITIVE(long)>(ptr_val);
}

// Basic template for accessing the length field of a non-array
// object.
template <class T>
auto uc_length_field(T ref) -> decltype(ref->UC_VAR(length))& {
  return ref->UC_VAR(length);
}

// add your overloads here
template <class E>
UC_PRIMITIVE(int)
uc_length_field(UC_ARRAY(E) array) {
  return uc_array_length(array);
}

// define your overloads for uc_add() here

// both numeric
template <class N1, class N2>
auto uc_add(N1 a, N2 b) -> decltype(a + b) {
  return a + b;
}
template <class N>
N uc_add(N a, N b) {
  return a + b;
}

// both strings
UC_PRIMITIVE(string) uc_add(UC_PRIMITIVE(string) a, UC_PRIMITIVE(string) b) {
  return a + b;
}

// one string one numeric
template <class N>
UC_PRIMITIVE(string)
uc_add(UC_PRIMITIVE(string) a, N b) {
  return a + std::to_string(b);
}

template <class N>
UC_PRIMITIVE(string)
uc_add(N a, UC_PRIMITIVE(string) b) {
  return std::to_string(a) + b;
}

// one string one boolean
UC_PRIMITIVE(string)
uc_add(UC_PRIMITIVE(string) a, UC_PRIMITIVE(boolean) b) {
  return a + (b ? "true" : "false");
}

UC_PRIMITIVE(string)
uc_add(UC_PRIMITIVE(boolean) a, UC_PRIMITIVE(string) b) {
  return (a ? "true" : "false") + b;
}

}  // namespace uc
