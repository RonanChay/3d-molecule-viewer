CC = clang
CFLAGS = -std=c99 -Wall -pedantic

# Location of your python3 header file
PYTHON3_HEADER = /Library/Frameworks/Python.framework/Versions/3.12/include/python3.12
# Location of your python3 language library
PYTHON3_LIB = /Library/Frameworks/Python.framework/Versions/3.12/lib

_molecule.so: libmol.so wrap molecule_wrap.o
	$(CC) -shared molecule_wrap.o -L$(PYTHON3_LIB) -lpython3.12 -L. -lmol -dynamiclib -o _molecule.so

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I $(PYTHON3_HEADER) -o molecule_wrap.o

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
