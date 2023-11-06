import molecule
from MolExceptions import InvalidSdf

'''
******************
*   CONSTANTS
******************
'''
 
header = ""

footer = """</svg>"""

offsetx = 500
offsety = 500

radius = {}
element_name = {}

'''
******************
*   CLASSES
******************
'''

# [Additional Helper] Point Class: Represents a cartesian 2-D point
# Members: x, y - The x and y coordinates of the Point
class Point ():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return '''x: %.2f\ny: %.2f\n''' % (self.x, self.y)

# Atom Class: Wrapper class for the atom structure in mol.h
# Members: atom - The c_atom structure
#          z - The z-coordinate of the Atom
# Methods: svg() - Creates an svg object string for the Atom
class Atom ():
    def __init__(self, cAtom):
        self.cAtom = cAtom
        self.z = cAtom.z

    def __str__(self):
        return '''Element: %s     Coordinates: (%.4f, %.4f, %.4f)\n''' % (self.cAtom.element, self.cAtom.x, self.cAtom.y, self.cAtom.z)
    
    def svg(self):
        x = self.cAtom.x * 100.0 + offsetx
        y = self.cAtom.y * 100.0 + offsety

        # Set colour and radius if element exists, otherwise set to default
        try:
            atomRadius = radius[self.cAtom.element]
            atomColour = element_name[self.cAtom.element]
        except KeyError:
            atomRadius = 30
            atomColour = "default"

        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (x, y, atomRadius, atomColour)

# Bond Class: Wrapper class for the bond structure in mol.h
# Members: bond - The c_bond structure
#          z - The z-coordinate of the Bond
# Methods: svg() - Creates an svg object string for the Bond
class Bond ():
    def __init__(self, cBond):
        self.cBond = cBond
        self.z = cBond.z
    
    def __str__(self):
        return '''a1: %d --> (%.4f, %.4f)\na2: %d --> (%.4f, %.4f)\nepairs: %d\nz: %.4f\nlength: %.4f\ndx: %.4f | dy: %.4f\n''' \
            % (self.cBond.a1, self.cBond.x1, self.cBond.y1, self.cBond.a2, self.cBond.x2, self.cBond.y2, self.cBond.epairs, self.cBond.z, self.cBond.len, self.cBond.dx, self.cBond.dy)

    def svg(self):
        # Calculate the position of the 4 corners of the bond using dx and dy
        bottomA1 = Point((self.cBond.x1 * 100 + offsetx) + self.cBond.dy * 10.0, (self.cBond.y1 * 100 + offsety) - self.cBond.dx * 10.0)
        topA1 = Point((self.cBond.x1 * 100 + offsetx) - self.cBond.dy * 10.0, (self.cBond.y1 * 100 + offsety) + self.cBond.dx * 10.0)
        topA2 = Point((self.cBond.x2 * 100 + offsetx) - self.cBond.dy * 10.0, (self.cBond.y2 * 100 + offsety) + self.cBond.dx * 10.0)
        bottomA2 = Point((self.cBond.x2 * 100 + offsetx) + self.cBond.dy * 10.0, (self.cBond.y2 * 100 + offsety) - self.cBond.dx * 10.0)

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' \
            % (bottomA1.x, bottomA1.y, topA1.x, topA1.y, topA2.x, topA2.y, bottomA2.x, bottomA2.y)

# Molecule Class: Wrapper class for the molecule structure in mol.h
# Methods: svg() - Creates an svg object string for the Molecule
#          parse() - Parses a .sdf file and populates the Molecule class
class Molecule (molecule.molecule):
    def __str__(self):
        # Atom details
        printStr = '''\natom_max: %d\natom_no: %d\natoms:\n\n''' % (self.atom_max, self.atom_no)
        for i in range(self.atom_no):
            printAtom = Atom(self.get_atom(i))
            printStr += str(printAtom) + "\n"
        
        # Bond details
        printStr += '''\nbond_max: %d\nbond_no: %d\nbonds:\n\n''' % (self.bond_max, self.bond_no)
        for i in range(self.bond_no):
            printBond = Bond(self.get_bond(i))
            printStr += str(printBond) + "\n"

        return printStr
        
    def svg(self):
        svgStr = header
        atomIndex = 0
        bondIndex = 0
        # Merge atoms and bonds by ascending z-value
        while atomIndex < self.atom_no and bondIndex < self.bond_no:
            if self.get_atom(atomIndex).z < self.get_bond(bondIndex).z:
                newAtom = Atom(self.get_atom(atomIndex))
                svgStr += newAtom.svg()
                atomIndex += 1
            else:
                newBond = Bond(self.get_bond(bondIndex))
                svgStr += newBond.svg()
                bondIndex += 1

        # Append all remaining atoms (if any)
        while atomIndex < self.atom_no:
            newAtom = Atom(self.get_atom(atomIndex))
            svgStr += newAtom.svg()
            atomIndex += 1
        # Append all remaining bonds (if any)
        while bondIndex < self.bond_no:
            newBond = Bond(self.get_bond(bondIndex))
            svgStr += newBond.svg()
            bondIndex += 1
        
        svgStr += footer
        
        return svgStr

    def parse(self, filePtr):
        i = 1
        for line in filePtr:
            # Skip header content
            if i <= 3:
                i += 1
                continue
            
            lineContent = line.split()
            try:
                # Atom and Bond number information
                if i == 4:
                    numAtoms = int(lineContent[0])
                    numBonds = int(lineContent[1])
                # Atom information
                elif i <= (4 + numAtoms):
                    self.append_atom(lineContent[3], float(lineContent[0]), float(lineContent[1]), float(lineContent[2]))
                # Bond information
                elif i <= (4 + numAtoms + numBonds):
                    self.append_bond(int(lineContent[0]) - 1, int(lineContent[1]) - 1, int(lineContent[2]))
                # End of .sdf file
                elif "END" in line:
                    break
                elif i > (4 + numAtoms + numBonds + 1):
                    raise Exception
            except:
                # print("Error: sdf file failed. Check to see if a valid sdf file was uploaded")
                raise InvalidSdf("SDF file failed to load. Check to see if a valid sdf file was uploaded")

            i += 1

    def rotate(self, pitch, yaw, roll):
        if (pitch != 0):
            mx = molecule.mx_wrapper(pitch, 0, 0)
            self.xform( mx.xform_matrix )
        if (yaw != 0):
            mx = molecule.mx_wrapper(0, yaw, 0)
            self.xform( mx.xform_matrix )
        if (roll != 0):
            mx = molecule.mx_wrapper(0, 0, roll)
            self.xform( mx.xform_matrix )
