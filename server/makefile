################################################
#     SET PYTHON VARIABLES HERE
################################################

# Python version [e.g: 3.12]
PYTHON_VERSION = <version>
# Path of your python header file [e.g: /Library/Frameworks/Python.framework/Versions/3.12/include/python3.12]
PYTHON_HEADER = <path>
# Path of your python language library [e.g: /Library/Frameworks/Python.framework/Versions/3.12/lib]
PYTHON_LIB = <path>

################################################

CC = clang
CFLAGS = -std=c99 -Wall -pedantic

_molecule.so: libmol.so wrap molecule_wrap.o
	$(CC) -shared molecule_wrap.o -L$(PYTHON_LIB) -lpython$(PYTHON_VERSION) -L. -lmol -dynamiclib -o _molecule.so

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I $(PYTHON_HEADER) -o molecule_wrap.o

wrap: mol.c mol.h
	swig -python molecule.i

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.h mol.c
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

clean:
	rm *.o *.so

rmsvg:
	rm *.svg
