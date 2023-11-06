#include "mol.h"

// NOTE: Detailed function comments and descriptions are in mol.h in an attempt to resemble API documentation

// Set atom data
void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

// Get atom data
void atomget(atom *atom, char element[3], double *x, double *y, double *z) {
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

// Set bond data
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->atoms = *atoms;
    bond->epairs = *epairs;

    compute_coords(bond);
}

// Get bond data
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

// Compute the coordinate data of the bond
void compute_coords(bond *bond) {
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2.0;
    bond->len = sqrt(pow((bond->x1 - bond->x2), 2) + pow((bond->y1 - bond->y2), 2));
    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}

// Allocate memory for a new molecule
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {
    molecule *newMol = (molecule *) malloc(sizeof(struct molecule));

    // Check for malloc() failure, return NULL if failed
    if (newMol == NULL) {
        printf("ERROR: malloc() failed, returning NULL\n");
        return NULL;
    }
    
    // Atoms allocation
    newMol->atom_max = atom_max;
    newMol->atom_no = 0;
    if (atom_max == 0) {
        newMol->atoms = NULL;
        newMol->atom_ptrs = NULL;
    } else {
        newMol->atoms = (atom *) malloc(atom_max * sizeof(struct atom));
        newMol->atom_ptrs = (atom **) malloc(atom_max * sizeof(struct atom *));
    }

    // Bonds allocation
    newMol->bond_max = bond_max;
    newMol->bond_no = 0;
    if (bond_max == 0) {
        newMol->bonds = NULL;
        newMol->bond_ptrs = NULL;
    } else {
        newMol->bonds = (bond *) malloc(bond_max * sizeof(struct bond));
        newMol->bond_ptrs = (bond **) malloc(bond_max * sizeof(struct bond *));
    }

    return newMol;
}

// Create copy of molecule
molecule *molcopy(molecule *src) {
    molecule *copyMol = molmalloc(src->atom_max, src->bond_max);

    // Check for malloc failure, returns NULL if failed
    if (copyMol == NULL) {
        return NULL;
    }

    // Copy atoms
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(copyMol, &(src->atoms[i]));
    }

    // Copy bonds
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(copyMol, &(src->bonds[i]));
    }

    return copyMol;
}

// Free molecule
void molfree(molecule *ptr) {
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    free(ptr);
}

// Append an atom to molecule
void molappend_atom(molecule *molecule, atom *atom) {
    int needRealloc = 0;    // Flags if need to call realloc() for atoms and atom_ptrs arrays

    // Check and update atom_max if arrays are full and need more space
    if (molecule->atom_max == 0) {
        molecule->atom_max = 1;
        needRealloc = 1;
    } else if (molecule->atom_no >= molecule->atom_max) {
        molecule->atom_max = molecule->atom_max * 2;
        needRealloc = 1;
    }
    // Reallocating arrays
    if (needRealloc == 1) {
        molecule->atoms = realloc(molecule->atoms, molecule->atom_max * sizeof(struct atom));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, molecule->atom_max * sizeof(struct atom *));
        // Check if realloc() fails, return without appending atom if failed
        if (molecule->atoms == NULL || molecule->atom_ptrs == NULL) {
            printf("ERROR: realloc() failed, returning without appending atom...\n");
            return;
        }

        // Rebind pointers to atoms according to index number
        for (int i = 0; i < molecule->atom_no; i++) {
            molecule->atom_ptrs[i] = &(molecule->atoms[i]);
        }
    }

    // Append atom
    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);
    (molecule->atom_no)++;
}

// Append bond to molecule
void molappend_bond(molecule *molecule, bond *bond) {
    int needRealloc = 0;    // Flags if need to call realloc() for bonds and bond_ptrs arrays

    // Check and update bond_max if arrays are full and need more space
    if (molecule->bond_max == 0) {
        molecule->bond_max = 1;
        needRealloc = 1;
    } else if (molecule->bond_no >= molecule->bond_max) {
        molecule->bond_max = molecule->bond_max * 2;
        needRealloc = 1;
    }
    // Reallocating arrays
    if (needRealloc == 1) {
        molecule->bonds = realloc(molecule->bonds, molecule->bond_max * sizeof(struct bond));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, molecule->bond_max * sizeof(struct bond *));
        // Check if realloc() fails, return without appending bond if failed
        if (molecule->bonds == NULL || molecule->bond_ptrs == NULL) {
            printf("ERROR: realloc() failed, returning without appending bond...\n");
            return;
        }

        // Rebind pointers to bonds according to index number
        for (int i = 0; i < molecule->bond_no; i++) {
            molecule->bond_ptrs[i] = &(molecule->bonds[i]);
        }
    }

    // Append bond
    bondset(&(molecule->bonds[molecule->bond_no]), &(bond->a1), &(bond->a2), &(molecule->atoms), &(bond->epairs));
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    (molecule->bond_no)++;
}

// Atom comparison function for qsort()
int compare_atom(const void * a1, const void * a2) {
    atom **atom_ptr1, **atom_ptr2;
    atom_ptr1 = (atom **) a1;
    atom_ptr2 = (atom **) a2;

    // Less than
    if ((*atom_ptr1)->z < (*atom_ptr2)->z) {
        return -1;
    }
    // Equal to
    if (fabs((*atom_ptr1)->z - (*atom_ptr2)->z) < 0.000001) {
        return 0;
    }
    // Greater than
    return 1;
}

// Bond comparison function for qsort()
int bond_comp(const void * b1, const void * b2) {
    bond **bond_ptr1 = (bond**) b1;
    bond **bond_ptr2 = (bond**) b2;

    // Less than
    if ((*bond_ptr1)->z < (*bond_ptr2)->z) {
        return -1;
    }
    // Equal to
    if (fabs((*bond_ptr1)->z - (*bond_ptr2)->z) < 0.000001) {
        return 0;
    }
    // Greater than
    return 1;
}

// Sort atoms and bonds in molecule based on z-coordinates
void molsort(molecule *molecule) {
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *), compare_atom);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *), bond_comp);
}

// Calculate x-axis rotation matrix
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

// Calculate y-axis rotation matrix
void yrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

// Calculate z-axis rotation matrix
void zrotation(xform_matrix xform_matrix, unsigned short deg) {
    double rad = (deg * M_PI) / 180.0;

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

// Apply rotation matrix to atoms of molecule
void mol_xform(molecule *molecule, xform_matrix matrix) {
    double xOld, yOld, zOld;    // Atom coordinates before rotation
    for (int i = 0; i < molecule->atom_no; i++) {
        xOld = molecule->atoms[i].x;
        yOld = molecule->atoms[i].y;
        zOld = molecule->atoms[i].z;

        molecule->atoms[i].x = (matrix[0][0] * xOld) 
                                + (matrix[0][1] * yOld) 
                                + (matrix[0][2] * zOld);
        molecule->atoms[i].y = (matrix[1][0] * xOld) 
                                + (matrix[1][1] * yOld) 
                                + (matrix[1][2] * zOld);
        molecule->atoms[i].z = (matrix[2][0] * xOld) 
                                + (matrix[2][1] * yOld) 
                                + (matrix[2][2] * zOld);
    }

    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&(molecule->bonds[i]));
    }
}

/*********************************
 *        NIGHTMARE MODE
 *********************************/

// Create rotations struct, calculate each rotation and return struct
rotations *spin(molecule *mol) {
    rotations *molSpin = malloc(sizeof(rotations));
    xform_matrix xRot, yRot, zRot;  // Matrices of rotation transformations about the axes

    for (int i = 0; i < 72; i++) {
        // Copy source molecule
        molSpin->x[i] = molcopy(mol);
        molSpin->y[i] = molcopy(mol);
        molSpin->z[i] = molcopy(mol);

        // Calculate rotations matrix
        xrotation(xRot, i * 5);
        yrotation(yRot, i * 5);
        zrotation(zRot, i * 5);

        // Apply transformation matrices
        mol_xform(molSpin->x[i], xRot);
        mol_xform(molSpin->y[i], yRot);
        mol_xform(molSpin->z[i], zRot);

        // Sort atoms and bonds of molecules
        molsort(molSpin->x[i]);
        molsort(molSpin->y[i]);
        molsort(molSpin->z[i]);
    }

    return molSpin;
}

// Free a rotations struct
void rotationsfree(rotations *rotations) {
    for (int i = 0; i < 72; i++) {
        molfree(rotations->x[i]);
        molfree(rotations->y[i]);
        molfree(rotations->z[i]);
    }
    free(rotations);
}
