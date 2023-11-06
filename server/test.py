import MolDisplay;
import molecule;

mol = MolDisplay.Molecule();

fp = open( 'water-3D-structure-CT1000292221.sdf' );
mol.parse( fp );
mol.sort();

print( mol );

mx = molecule.mx_wrapper(90,0,0);
mol.xform( mx.xform_matrix );

print( mol );

