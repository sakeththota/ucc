CORRECT_TESTS := $(wildcard tests/*.uc)
PHASE4_TESTS := tests/default.uc tests/equality.uc tests/hello.uc tests/use_before_decl.uc
PHASE5_TESTS := $(filter-out $(PHASE4_TESTS),$(CORRECT_TESTS))
LIB_DIR := .
PYTHON := python3
CXX := g++
CXXFLAGS := -g --std=c++17 -pedantic

# Check for valgrind
export VALGRIND :=
ifneq "$(shell command -v valgrind 2> /dev/null)" ""
  export VALGRIND := valgrind -q --leak-check=full --error-exitcode=1
endif

all: test life typedecls typedefs polymorph

test: phase1 phase2 phase3 phase4 phase5

phase1: $(CORRECT_TESTS:.uc=.phase1)

phase2: $(CORRECT_TESTS:.uc=.phase2)

phase3: $(CORRECT_TESTS:.uc=.phase3)

phase4: PHASE = 4
phase4: $(PHASE4_TESTS:.uc=.phase45)

phase5: PHASE = 5
phase5: $(PHASE5_TESTS:.uc=.phase45)

%.phase1:
	@echo "Running Phase 1 test on $(@:.phase1=.uc)..."
	$(PYTHON) ucc.py -C --backend-phase=1 $(@:.phase1=.uc)
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -c -o $(@:.phase1=_phase1.o) $(@:.phase1=_phase1.cpp)
	@echo

%.phase2:
	@echo "Running Phase 2 test on $(@:.phase2=.uc)..."
	$(PYTHON) ucc.py -C --backend-phase=2 $(@:.phase2=.uc)
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -c -o $(@:.phase2=_phase2.o) $(@:.phase2=_phase2.cpp)
	@echo

%.phase3:
	@echo "Running Phase 3 test on $(@:.phase3=.uc)..."
	$(PYTHON) ucc.py -C --backend-phase=3 $(@:.phase3=.uc)
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o $(@:.phase3=_phase3.exe) $(@:.phase3=_phase3.cpp)
	$(@:.phase3=_phase3.exe)
	@echo

%.phase45:
	@echo "Running Phase $(PHASE) test on $(@:.phase45=.uc)..."
	$(PYTHON) ucc.py -C $(@:.phase45=.uc)
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o $(@:.phase45=.exe) $(@:.phase45=.cpp)
	$(VALGRIND) $(@:.phase45=.exe) 20 10 5 2 > $(@:.phase45=.run)
	diff -q $(@:.phase45=.run.correct) $(@:.phase45=.run)
	@echo

life:
	@echo "Testing life.uc..."
	$(PYTHON) ucc.py -C life.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o life.exe life.cpp
	$(VALGRIND) ./life.exe | diff -q - life_test.correct
	@echo

deque:
	@echo "Testing deque.uc..."
	$(PYTHON) ucc.py -C deque.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o deque.exe deque.cpp
	$(VALGRIND) ./deque.exe | diff -q - deque.correct
	@echo

typedecls:
	@echo "Testing typedecls.uc..."
	$(PYTHON) ucc.py -C typedecls.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o typedecls.exe typedecls.cpp
	$(VALGRIND) ./typedecls.exe | diff -q - typedecls.correct
	@echo

typedefs:
	@echo "Testing typedefs.uc..."
	$(PYTHON) ucc.py -C typedefs.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o typedefs.exe typedefs.cpp
	$(VALGRIND) ./typedefs.exe | diff -q - typedefs.correct
	@echo

polymorph:
	@echo "Testing polymorph.uc..."
	$(PYTHON) ucc.py -C polymorph.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o polymorph.exe polymorph.cpp
	$(VALGRIND) ./polymorph.exe | diff -q - polymorph.correct
	@echo

merge_sort:
	@echo "Testing merge_.uc..."
	$(PYTHON) ucc.py -C merge_sort.uc
	$(CXX) $(CXXFLAGS) -I$(LIB_DIR) -o merge_sort.exe merge_sort.cpp
	$(VALGRIND) ./merge_sort.exe
	@echo

STYLE_SOURCES := $(filter-out ucparser.py,$(wildcard uc*.py))
# Pylint 2.6.0 has false positives for E1136
PYLINT_FLAGS := --max-args=6 --max-module-lines=1500 -d e1136

style: style-pycode style-pydoc style-pylint

style-pycode:
	pycodestyle $(STYLE_SOURCES)

style-pydoc:
	pydocstyle $(STYLE_SOURCES)

style-pylint:
	pylint $(PYLINT_FLAGS) $(STYLE_SOURCES)

clean:
	rm -f $(CORRECT_TESTS:.uc=.cpp) tests/*.o tests/*.exe tests/*.run
	rm -f life.cpp life.exe
	rm -f typedefs.cpp typedefs.exe
	rm -f typedecls.cpp typedecls.exe
	rm -f polymorph.cpp polymorph.exe
	rm -rf -f tests/*.dSYM *.dSYM
