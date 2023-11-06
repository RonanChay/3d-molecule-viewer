import sqlite3
import MolDisplay
import os
# import molecule
from MolExceptions import DuplicateEntry

class Database:
    # Initialise connection to database. Reset database if reset=True
    def __init__(self, reset=False):
        if (reset and os.path.exists( 'molecules.db' )):
            os.remove("molecules.db")
        self.conn = sqlite3.connect("molecules.db")

    # Create the tables of molecules.db
    def create_tables(self):
        # Elements table
        # Check if table exists
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'Elements';
        ''').fetchall()
        # Create table if doesnt exist
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE Elements
                (   ELEMENT_NO       INTEGER                   NOT NULL,
                    ELEMENT_CODE     VARCHAR(3)   PRIMARY KEY  NOT NULL,
                    ELEMENT_NAME     VARCHAR(32)               NOT NULL,
                    COLOUR1          CHAR(6)                   NOT NULL,
                    COLOUR2          CHAR(6)                   NOT NULL,
                    COLOUR3          CHAR(6)                   NOT NULL,
                    RADIUS           DECIMAL(3)                NOT NULL
                );
            ''')

        # Atoms table
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'Atoms';
        ''').fetchall()
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE Atoms
                (   ATOM_ID         INTEGER         PRIMARY KEY   AUTOINCREMENT   NOT NULL,
                    ELEMENT_CODE    VARCHAR(3)                                    NOT NULL,
                    X               DECIMAL(7, 4)                                 NOT NULL,
                    Y               DECIMAL(7, 4)                                 NOT NULL,
                    Z               DECIMAL(7, 4)                                 NOT NULL,
                    FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
                );
            ''')
        
        # Bonds table
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'Bonds';
        ''').fetchall()
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE Bonds
                (   BOND_ID INTEGER   PRIMARY KEY   AUTOINCREMENT   NOT NULL,
                    A1      INTEGER                                 NOT NULL,
                    A2      INTEGER                                 NOT NULL,
                    EPAIRS  INTEGER                                 NOT NULL
                );
            ''')
        
        # Molecules table
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'Molecules';
        ''').fetchall()
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE Molecules
                (   MOLECULE_ID INTEGER   PRIMARY KEY   AUTOINCREMENT   NOT NULL,
                    NAME        TEXT      UNIQUE                        NOT NULL    
                );
            ''')

        # MoleculeAtom table
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'MoleculeAtom';
        ''').fetchall()
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE MoleculeAtom
                (   MOLECULE_ID INTEGER     NOT NULL,
                    ATOM_ID     INTEGER     NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                    FOREIGN KEY (ATOM_ID)     REFERENCES Atoms(ATOM_ID)
                );
            ''')
        
        # MoleculeBond table
        tableExists = self.conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            AND name = 'MoleculeBond';
        ''').fetchall()
        if (tableExists == []):
            self.conn.execute('''
                CREATE TABLE MoleculeBond
                (   MOLECULE_ID INTEGER     NOT NULL,
                    BOND_ID     INTEGER     NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, BOND_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                    FOREIGN KEY (BOND_ID)     REFERENCES Bonds(BOND_ID)
                );
            ''')
    
    # Redefine the __setitem__ method to insert rows with values <values> in the table <table>
    def __setitem__(self, table, values):
        # Create parameter string
        valuesString = "("
        for _ in values:
            valuesString += "?, "
        valuesString = valuesString[:len(valuesString) - 2] + ")"

        self.conn.execute('''
            INSERT INTO %s
            VALUES      %s;
        ''' % (table, valuesString), values)

    # Add an atom <atom> in the molecule <molname> to the relevant tables
    def add_atom(self, molname, atom):
        # Insert atom into Atoms table
        self["Atoms"] = (None, atom.cAtom.element, atom.cAtom.x, atom.cAtom.y, atom.cAtom.z)

        # Get MOLECULE_ID and ATOM_ID of new atom
        molID = self.conn.execute('''
            SELECT MOLECULE_ID FROM Molecules
            WHERE NAME = '%s';
        ''' % (molname)).fetchone()
        atomID = self.conn.execute('''
            SELECT max(ATOM_ID) FROM Atoms;
        ''').fetchone()
        
        # Insert linking data in MoleculeAtom table
        self["MoleculeAtom"] = (molID[0], atomID[0])
    
    # Add a bond <bond> in the molecule <molname> to the relevant tables
    def add_bond(self, molname, bond):
        # Insert bond into Bonds table
        self["Bonds"] = (None, bond.cBond.a1, bond.cBond.a2, bond.cBond.epairs)

        # Get MOLECULE_ID and BOND_ID of new bond
        molID = self.conn.execute('''
            SELECT MOLECULE_ID FROM Molecules
            WHERE NAME = '%s';
        ''' % (molname)).fetchone()
        bondID = self.conn.execute('''
            SELECT max(BOND_ID) FROM Bonds;
        ''').fetchone()

        # Insert linking data in MoleculeBond table
        self["MoleculeBond"] = (molID[0], bondID[0])
    
    # Add a molecule <mol> called <name> into the relevant tables
    def add_molecule(self, name, newMol):
        try:
            # Insert new molecule into Molecules table
            self["Molecules"] = (None, name)
        except:
            raise DuplicateEntry("Entry already exists in database")

        # Insert each atom using add_atom()
        for i in range(newMol.atom_no):
            atom = MolDisplay.Atom(newMol.get_atom(i))
            self.add_atom(name, atom)
        
        # Insert each bond using add_bond()
        for i in range(newMol.bond_no):
            bond = MolDisplay.Bond(newMol.get_bond(i))
            self.add_bond(name, bond)

    # Add an element to the Elements table
    def add_element(self, num, symbol, name, c1, c2, c3, radius):
        try:
            self['Elements'] = (num, symbol, name, c1, c2, c3, radius)
        except:
            raise DuplicateEntry("Entry already exists in database")
    
    # Remove an element with element_code <symbol> from Elements table
    def remove_element(self, symbol):
        self.conn.execute('''
            DELETE FROM Elements
            WHERE ELEMENT_CODE = '%s';
        ''' % (symbol))
    
    # Load a new molecule called <name> from the table into a MoDisplay.Molecule() object
    def load_mol(self, name):
        newMol = MolDisplay.Molecule()

        # Get atom data from relevant tables
        atomData = self.conn.execute('''
            SELECT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z
            FROM Atoms INNER JOIN MoleculeAtom, Molecules 
            ON (MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID) AND (MoleculeAtom.ATOM_ID = Atoms.ATOM_ID)
            WHERE Molecules.NAME = '%s'
            ORDER BY Atoms.ATOM_ID ASC;
        ''' % (name)).fetchall()
        
        # Get bond data from relevant tables
        bondData = self.conn.execute('''
            SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS
            FROM Bonds INNER JOIN MoleculeBond, Molecules 
            ON (MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID) AND (MoleculeBond.BOND_ID = Bonds.BOND_ID)
            WHERE Molecules.NAME = '%s'
            ORDER BY Bonds.BOND_ID ASC;
        ''' % (name)).fetchall()

        # Populate atoms in newMol
        for atom in atomData:
            newMol.append_atom(atom[0], float(atom[1]), float(atom[2]), float(atom[3]))
        
        # Populate bonds in newBond
        for bond in bondData:
            newMol.append_bond(int(bond[0]), int(bond[1]), int(bond[2]))

        return newMol

    # Get list of all molecules in db with the number of atoms and bonds in each molecule
    def get_molecules(self):
        atomData = self.conn.execute('''
            SELECT COUNT(ATOM_ID)
            FROM MoleculeAtom
            GROUP BY MOLECULE_ID
            ORDER BY MOLECULE_ID ASC;
        ''').fetchall()

        bondData = self.conn.execute('''
            SELECT COUNT(BOND_ID)
            FROM MoleculeBond
            GROUP BY MOLECULE_ID
            ORDER BY MOLECULE_ID ASC;
        ''').fetchall()

        moleculeNames = self.conn.execute('''
            SELECT MOLECULE_ID, NAME
            FROM Molecules
            ORDER BY MOLECULE_ID ASC;
        ''').fetchall()
        
        # Create list of dictionaries for each molecule
        molList = []
        i = 0
        for mol in moleculeNames:
            print(mol)
            molList.append({"id": mol[0], "name": mol[1], "atomNum": atomData[i][0], "bondNum": bondData[i][0]})
            i += 1
        
        return molList
    
    # Get list of all elements
    def get_elements(self):
        elementData = self.conn.execute('''
            SELECT ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS 
            FROM Elements
            ORDER BY ELEMENT_NO ASC;
        ''').fetchall()

        elementList = []
        for el in elementData:
            elementList.append({
                "number": el[0],
                "code": el[1],
                "name": el[2],
                "colour1": el[3],
                "colour2": el[4],
                "colour3": el[5],
                "radius": el[6]
            })

        return elementList
    
    # Create radius dictionary using Elements table data
    def radius(self):
        radiusRows = self.conn.execute('''
            SELECT ELEMENT_CODE, RADIUS
            FROM Elements;
        ''').fetchall()

        radius = dict(radiusRows)

        return radius
    
    # Create element_name dictionary using Elements table data
    def element_name(self):
        elementNamesRows = self.conn.execute('''
            SELECT ELEMENT_CODE, ELEMENT_NAME
            FROM Elements;
        ''').fetchall()

        elementNames = dict(elementNamesRows)

        return elementNames
    
    # Create radial gradients svg string using data from Elements table
    def radial_gradients(self):
        # Default colour for elements that are not in db
        radialGradientSVG = """ 
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%"> 
    <stop offset="0%%" stop-color="#%s"/> 
    <stop offset="50%%" stop-color="#%s"/> 
    <stop offset="100%%" stop-color="#%s"/> 
  </radialGradient>""" % ("default", "E2E8F0", "718096", "1a202c")

        # Get colour and name data from Elements
        elements = self.conn.execute('''
            SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
            FROM Elements;
        ''').fetchall()

        # Create radialGradientsSVG string for each element
        for element in elements:
            radialGradientSVG += """ 
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%"> 
    <stop offset="0%%" stop-color="#%s"/> 
    <stop offset="50%%" stop-color="#%s"/> 
    <stop offset="100%%" stop-color="#%s"/> 
  </radialGradient>""" % (element[0], element[1], element[2], element[3])

        radialGradientSVG += "\n"

        return radialGradientSVG
    
    # Helper method to commit transactions to database
    def commit_db(self):
        self.conn.commit()
        