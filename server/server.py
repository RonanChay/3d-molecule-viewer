import sys
import MolSql
import MolDisplay
from MolExceptions import InvalidSdf, DuplicateEntry
from io import TextIOWrapper
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib

# List of files that client can request
public_files = [
    "/display.html", 
    "/display.css", 
    "/display.js", 
    "/elements.html", 
    "/elements.css", 
    "/elements.js", 
    "/molecules.html", 
    "/molecules.css", 
    "/molecules.js"
]
db = MolSql.Database(reset=False)
db.create_tables()

# MolHandler Class: Extends BaseHTTPRequestHandler class to provide own do_GET and do_POST methods
class MolHandler(BaseHTTPRequestHandler):
    '''
    ' GET METHOD
    '''
    def do_GET(self):
        # Send files to client
        if self.path in public_files:
            filename = "../client/components" + self.path
            file_ptr = open(filename)
            webform = file_ptr.read()
            file_ptr.close()

            page_type = "text/"
            if ".html" in filename:
                page_type += "html"
            elif ".css" in filename:
                page_type += "css"
            elif ".js" in filename:
                page_type += "javascript"

            self.set_header_info(200, page_type, len(webform))
            self.wfile.write(bytes(webform, "utf-8"))

        # Get list of molecules in database and send to client
        elif "/get-molecules" in self.path:
            moleculeList = db.get_molecules()
            jsonStr = json.dumps(moleculeList)
            print(jsonStr)

            self.set_header_info(200, "application/json", len(jsonStr))
            self.wfile.write(bytes(jsonStr, "utf-8"))

        # Get list of elements in database and send to client
        elif "/get-elements" in self.path:
            elementList = db.get_elements()
            print(elementList)
            jsonStr = json.dumps(elementList)

            self.set_header_info(200, "application/json", len(jsonStr))
            self.wfile.write(bytes(jsonStr, "utf-8"))

        # Path other than public_files is requested
        else:
            print(self.path)
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Error 404: Page does not exist. Ensure you typed the correct URL.", "utf-8"))
    
    '''
    ' POST METHOD
    '''
    def do_POST(self):
        # Upload an sdf and add molecule to database
        if "/sdf-upload" in self.path:
            formPtr = TextIOWrapper(self.rfile)
            
            # Skip header content
            for i in range(4):
                formPtr.readline()

            statusCode = 200    # assume valid at start, check if invalid
            message = "success"

            # Parse sdf
            newMol = MolDisplay.Molecule()
            try:
                newMol.parse(formPtr)
            except InvalidSdf as err:
                message = err.message
                statusCode = 400
            else:
                # Get molecule name
                molName = ""
                while molName == "":
                    line = formPtr.readline()
                    if 'name="molName"' in line:
                        formPtr.readline()
                        molName = formPtr.readline().rstrip().title()

                if (len(molName) == 0 or not molName.isalpha):
                    statusCode = 400
                    message = "Invalid molecule name (Should be letters only)"
                else:
                    # Add molecule to database
                    try:
                        db.add_molecule(molName, newMol)
                        db.commit_db()
                    except DuplicateEntry as err:
                        statusCode = 400
                        message = err.message
            
            self.set_header_info(statusCode, 'text/plain', len(message))
            self.wfile.write(bytes(message, "utf-8"))

        # Get svg string for molecule
        elif "/get-svg" in self.path:
            postvars = self.get_postvars()

            molName = postvars["name"][0]

            newMol = db.load_mol(molName)
            newMol.sort()
            svgContent = self.get_svg(newMol)

            self.set_header_info(200, 'text/html', len(svgContent))
            self.wfile.write(bytes(svgContent, "utf-8"))

        # Rotate and get svg string for molecule
        elif "/rotate-svg" in self.path:
            postvars = self.get_postvars()

            molName = postvars["name"][0]
            try:
                xRot = int(postvars["xRot"][0])
                yRot = int(postvars["yRot"][0])
                zRot = int(postvars["zRot"][0])
            except ValueError:
                self.send_bad_request()
            else:
                if (xRot < 0 or yRot < 0 or zRot < 0):
                    self.send_bad_request()
                else:
                    newMol = db.load_mol(molName)
                    newMol.sort()
            
                    newMol.rotate(xRot, yRot, zRot)

                    svgContent = self.get_svg(newMol)

                    self.set_header_info(200, 'text/html', len(svgContent))
                    self.wfile.write(bytes(svgContent, "utf-8"))

        # Add an element to the database
        elif "/add-element" in self.path:
            postvars = self.get_postvars()
            isValid = True

            # Get element number and radius
            try:
                number = int(postvars["number"][0])
                radius = int(postvars["radius"][0])
            except ValueError:
                isValid = False
            if (radius < 1 or number < 1 or number > 118):
                isValid = False

            # Get element code
            code = postvars["code"][0].title()
            if (len(code) < 1 or len(code) > 2 or not code.isalpha()):
                isValid = False

            # Get element name
            name = postvars["name"][0].title()
            if (len(name) == 0 or not name.isalpha()):
                isValid = False

            # Get 3 element colours
            colour1 = postvars["colour1"][0].upper()
            colour2 = postvars["colour2"][0].upper()
            colour3 = postvars["colour3"][0].upper()
            try:
                int(colour1, 16)
                int(colour2, 16)
                int(colour3, 16)
            except ValueError:
                isValid = False
                
            if (len(colour1) != 6 or len(colour2) != 6 or len(colour3) != 6):
                isValid = False

            # Add element to database
            if isValid:
                try:
                    db.add_element(number, code, name, colour1, colour2, colour3, radius)
                    db.commit_db()
                    message = "successful"
                    self.set_header_info(200, 'text/plain', len(message))
                    self.wfile.write(bytes(message, "utf-8"))
                except DuplicateEntry as err:
                    message = "error - duplicate (" + err.message + ")"
                    self.set_header_info(400, 'text/plain', len(message))
                    self.wfile.write(bytes(message, "utf-8"))
            else:
                self.send_bad_request()

        # Remove an element from database
        elif "/remove-element" in self.path:
            postvars = self.get_postvars()

            symbol = postvars["code"][0]

            db.remove_element(symbol)
            db.commit_db()

            message = "successful"
            self.set_header_info(200, 'text/plain', len(message))
            self.wfile.write(bytes(message, "utf-8"))

        # Bad request - Should not reach here typically
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: Page does not exist. Failed POST request...", "utf-8"))

    # Helper method to send bad message to client when input is invalid/failed
    def send_bad_request(self):
        message = "not successful"
        self.set_header_info(400, 'text/plain', len(message))
        self.wfile.write(bytes(message, "utf-8"))
    
    # Helper method to get the variables sent by client to server
    def get_postvars(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        return urllib.parse.parse_qs( body.decode( 'utf-8' ) )
    
    # Helper method to generate svg string for a molecule
    def get_svg(self, newMol):
        MolDisplay.radius = db.radius()
        MolDisplay.element_name = db.element_name()
        MolDisplay.header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">""" + db.radial_gradients()

        return newMol.svg()

    # Helper method to set the header info before sending response to client
    def set_header_info(self, code, type, length):
        self.send_response(code)
        self.send_header("Content-type", type)
        self.send_header("Content-length", length)
        self.end_headers()


if __name__ == "__main__":
    # Run the server at port specified by command-line argument
    if len(sys.argv) == 2:
        httpd = HTTPServer(('localhost', int(sys.argv[1]) ), MolHandler)
        httpd.serve_forever()
    else:
        print("ERROR: Invalid number of command-line arguments - Enter the listening port number as the first command-line argument after the program name")
