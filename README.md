# uC Code Generator 

uC Code Generator is a uC to C++ source-to-source compiler written in Python.

## Usage

Here is an example uC program ```hello.uc``` written according to the following language specification

[uC Language Specification](https://eecs390.github.io/uc-language/)

```c
void main(string[] args)() {
  println("Hello world!");
}
```

In order to compile the program to C++, we can run the following command using the entry point ```ucc.py```

```bash
python3 ucc.py -C hello.uc
```

We can then compile and run the code produced in ```hello.cpp``` as we would any C++ program.

```bash
g++ -g --std=c++17 -pedantic -I. -o hello.exe hello.cpp
./hello.exe
Hello World!
```