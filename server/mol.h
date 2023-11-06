#ifndef _mol_h
#define _mol_h

#ifndef M_PI
#define M_PI 3.141592653589793
#endif

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

/**
 * Structure that describes an atom and its position in 3-dimensional space
 * Items: 
 *  - char element[3]
 *  - double x, y, z
 */
typedef struct atom {

    // Null-terminated string representing the element name of the atom
    char element[3];

    // Position in Angstroms (Å) of the atom relative to a common origin for a molecule
    double x, y, z;
} atom;

/**
 * Defines a structure that represents a co-valent bond between two atoms.
 * Items:
 *  - atom *a1, *a2: Indices of the two atoms in the co-valent bonds
 *  - unsigned char epairs: Number of electron pairs in the bond
 *  - atom *atoms: Pointer to array of atoms
 *  - double x1, x2, y1, y2: x-y coordinates of a1 and a2
 *  - double z: Average z-coordinate of a1 and a2
 *  - double len: Distance between a1 and a2
 *  - double dx, dy: Change in x/y between a1 and a2 per unit length
 */
typedef struct bond {  

    // Index of the atom in the co-valent bonds
    unsigned short a1, a2;

    // Number of electron pairs in the bond
    unsigned char epairs;

    // Pointer to array of atoms
    atom *atoms;

    // x-y coordinates of the atom
    double x1, x2, y1, y2;

    // Average z-coordinate of a1 and a2
    double z;

    // Distance between a1 and a2
    double len;

    // Change in x/y between a1 and a2 per unit length
    double dx, dy; 
} bond;

/**
 * Represents a molecule which consists of zero or more atoms, and zero or more bonds
 * Items:
 *  - unsigned short atom_max, atom_no
 *  - atom *atoms, **atom_ptrs
 *  - unsigned short bond_max, bond_no
 *  - bond *bonds, **bond_ptrs
 */
typedef struct molecule {

    // Non-negative integer that records the dimensionality of an array pointed to by atoms
    unsigned short atom_max;
    // Number of atoms currently stored in the array atoms
    unsigned short atom_no;

    // Array of atoms in the molecule
    atom *atoms;
    // Array of pointers to the atoms in the molecule
    atom **atom_ptrs;

    // Non-negative integer that records the dimensionality of an array pointed to by bonds
    unsigned short bond_max;
    // Number of bonds currently stored in the array bonds
    unsigned short bond_no;

    // Array of bonds in the molecule
    bond *bonds;
    // Array of pointers to the bonds in the molecule
    bond **bond_ptrs;
} molecule;

// 3-d transformation matrix for molecule rotations
typedef double xform_matrix[3][3];

/**
 * @brief Sets an atom's values to the specified values
 * 
 * @param atom Atom to copy data to (destination)
 * @param element Element to copy into atom
 * @param x x-coordinate to copy into atom
 * @param y y-coordinate to copy into atom
 * @param z z-coordinate to copy into atom
 */
void atomset( atom *atom, char element[3], double *x, double *y, double *z );

/**
 * @brief Gets the values of a specified atom
 * 
 * @param atom Atom to copy data from (source)
 * @param element element to get from atom
 * @param x x-coordinate to get from atom
 * @param y y-coordinate to get from atom
 * @param z z-coordinate to get from atom
 */
void atomget( atom *atom, char element[3], double *x, double *y, double *z );

/**
 * @brief Sets a bond's values to the specified values
 * 
 * @param bond Bond to copy data to (destination)
 * @param a1 atom 1 to store into bond
 * @param a2 atom 2 to store into bond
 * @param atoms Pointer to atoms array
 * @param epairs Number of epairs to store into bond
 */
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );

/**
 * @brief Gets the values of a specified bond
 * 
 * @param bond Bond to copy data from (source)
 * @param a1 atom 1 to copy from bond
 * @param a2 atom 2 to copy from bond
 * @param atoms Pointer to atoms array
 * @param epairs Number of epairs to copy from bond
 */
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );

/**
 * @brief Computes the z, x1, y1, x2, y2, len, dx, and dy values of the bond 
 * 
 * @param bond Source bond
 */
void compute_coords( bond *bond );

/**
 * @brief Allocates memory for a moleule using the specified atom_max and bond_max values.
 * Returns NULL if malloc() fails
 * 
 * @param atom_max Max size of the atoms and atom_ptrs arrays
 * @param bond_max Max size of the bonds and bond_ptrs arrays
 * @return molecule* 
 */
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max );

/**
 * @brief Creates a copy of the molecule data and returns a pointer to the new copy molecule. 
 * Returns NULL is malloc fails
 * 
 * @param src Source molecule
 * @return molecule* New copied molecule
 */
molecule *molcopy( molecule *src );

/**
 * @brief Frees the memory allocated to a molecule
 * 
 * @param ptr Molecule to be freed
 */
void molfree( molecule *ptr );

/**
 * @brief Appends an atom to the atoms and atom_ptrs array in a molecule. 
 * Returns before appending atoms if realloc() fails
 * 
 * @param molecule Source molecule
 * @param atom Atom to be appended
 */
void molappend_atom( molecule *molecule, atom *atom );

/**
 * @brief Appends a bond to the bonds and bond_ptrs array in a molecule. 
 * Returns before appending bonds if realloc() fails
 * 
 * @param molecule Source molecule
 * @param bond Bond to be appended
 */
void molappend_bond( molecule *molecule, bond *bond );

/**
 * @brief Compar() function for atoms to be used in qsort() for molsort() function
 * 
 * @param a1 pointer to atom 1
 * @param a2 pointer to atom 2
 * @return int 
 */
int compare_atom( const void *a1, const void *a2 );

/**
 * @brief Compar() function for bonds to be used in qsort() for molsort() function
 * 
 * @param a pointer to bond 1
 * @param b pointer to bond 1
 * @return int 
 */
int bond_comp( const void *a, const void *b );

/**
 * @brief Sorts the arrays based on the z-coordinate of the atoms/bonds, from lowest to highest. 
 * For bonds, z-coordinate = average z-coordinate between 2 atoms
 * 
 * @param molecule Source molecule
 */
void molsort( molecule *molecule );

/**
 * @brief Calculates and sets the values of the rotation matrix for a rotation of <deg> degrees along the x-axis
 * 
 * @param xform_matrix Transformatin matrix for a rotation along the x-axis
 * @param deg Degree of the rotation
 */
void xrotation( xform_matrix xform_matrix, unsigned short deg );

/**
 * @brief Calculates and sets the values of the rotation matrix for a rotation of <deg> degrees along the y-axis.
 * 
 * @param xform_matrix Transformatin matrix for a rotation along the y-axis
 * @param deg Degree of the rotation
 */
void yrotation( xform_matrix xform_matrix, unsigned short deg );

/**
 * @brief Calculates and sets the values of the rotation matrix for a rotation of <deg> degrees along the z-axis.
 * 
 * @param xform_matrix Transformatin matrix for a rotation along the z-axis
 * @param deg Degree of the rotation
 */
void zrotation( xform_matrix xform_matrix, unsigned short deg );

/**
 * @brief Applies the transformation matrix to all the atoms of the molecule using vector multiplication
 * 
 * @param molecule Molecule to rotate
 * @param matrix Transformation matrix for the rotation
 */
void mol_xform( molecule *molecule, xform_matrix matrix );

/**
 * @brief Wrapper typedef for swig molecule.i
 */
typedef struct mx_wrapper {
    xform_matrix xform_matrix;
} mx_wrapper;

/*********************************
 *        NIGHTMARE MODE
 *********************************/

/**
 * @brief Represents the rotations of a given molecule around the x, y and z axes in 5 degree increments
 * Items:
 *  - molecule *x[72]: Each 5 degree rotation of a molecule about the x-axis
 *  - molecule *y[72]: Each 5 degree rotation of a molecule about the y-axis
 *  - molecule *z[72]: Each 5 degree rotation of a molecule about the z-axis
 */
typedef struct rotations {
    molecule *x[72]; 
    molecule *y[72]; 
    molecule *z[72]; 
} rotations;

/**
 * @brief Allocate memory for a rotations structure, create molecules using molcopy 
 * applied to the provided mol, and add their pointers to the x, y, and z members of the rotations 
 * structure.
 * 
 * @param mol Source molecule
 * @return rotations* 
 */
rotations *spin( molecule *mol );

/**
 * @brief Frees memory allocated to a rotations struct
 * 
 * @param rotations Rotations struct to be freed
 */
void rotationsfree( rotations *rotations );

#endif
