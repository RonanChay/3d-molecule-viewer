# 3d-molecule-viewer

This project is a simple full-stack web application that will display molecules in 3-dimensions.
It parses molecule sdf files uploaded to the website, stores the atom and molecule information
in an SQL database, and generates svg images of the uploaded molecules that can be viewed on the
site.

* Backend written in Python using Http.server and C
* Frontend written in HTML/CSS and JavaScript with JQuery
* Molecule and atom data is stored in an SQLite database in the server directory

The Python server will run locally using the port number given as a command-line
argument

## Features

  - Upload a molecule sdf file to the website to accumulate a list of molecules
  - View any molecule from the list of uploaded molecules from any angle
  - Set the colours of the elements in the molecule


## Dependencies

You will need to install the following to compile and run the project:

1. clang + GNU Make
2. Python3
3. Swig

## How to Run

### 1. Compile the C files with clang and swig using the makefile
- Go to the server/makefile and set the python variables as instructed in the makefile.
  - You will need the version of your python install, and the paths to the python header file and language library
- Execute the following commands:

```
cd server
make
```
This will compile the C source files into wrapper files that can be used by the Python server

### 2. Run the server
- Still in the server directory, run the server by executing the following command:

```
python3 server.py <port>
```
where `<port>` is the port number that the server will run on

### 3. Open the website on a browser
- Open your favourite browser and go to `localhost:<port>/display` where `<port>` is the port number used in Step 2


## Makefile commands

The following commands are available through the makefile provided in the server directory:
* `make` : Compile all the C files using swig and clang
* `make clean` : Remove all the compiled C files
* `make rmsvg` : Remove all the svg files in the server directory 