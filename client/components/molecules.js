$(document).ready(
    function () {
        // Update molecule table
        getMoleculeList();

        // Add onClick event to add molecule button
        $("#add-molecule-button").click( () => {
            if (isFieldEmpty() == false) {
                // Get form data
                var fileObj = $("#sdf-file")[0].files[0]
                var form = new FormData()
                form.append("form", fileObj)
                form.append("molName", $("#molecule-name").val())
                
                // Ajax POST Request to upload sdf file
                $.ajax( {
                    url: "/sdf-upload",
                    type: "POST",
                    data: form,
                    processData: false,
                    contentType: false,
                    success: function () {
                        alert("Successfully uploaded sdf file! Molecule was added to the database.");
                        getMoleculeList();
                    },
                    error: function() {
                        alert("Upload failed... Ensure that sdf file is correct and a valid molecule name was entered (letters only).");
                    }
                });
            } else {
                alert("There are empty fields! Ensure that a valid .sdf file and a molecule name is entered before adding a molecule.")
            }
        })
    }
);


// GET request to get list of molecules in database and refresh the molecules table
function getMoleculeList() {
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/get-molecules",
        success: function (data) {
            refreshMoleculesTable(JSON.parse(JSON.stringify(data)));
        }
    });
}

// Update the molecules table with rows of molecules
function refreshMoleculesTable(molecules) {
    // Empty current table and add header row
    $("#molecule-table").empty().append(
        '<tr> <th> Molecule ID </th> <th> Molecule Name </th> <th> Number of Atoms </th> <th> Number of Bonds </th> </tr>'
    );

    // Append molecule rows
    for (let i = 0; i < molecules.length; i++) {
        var mol = molecules[i];
        var tableRow = $('<tr>');
        tableRow.attr('id', mol.code);
        tableRow.append(
            '<td> ' + mol.id + ' </td> <td> ' + mol.name + ' </td> <td> ' + mol.atomNum + ' </td> <td> ' + mol.bondNum + ' </td> '
        );

        tableRow.appendTo("#molecule-table");
    }
}

// Check if there are empty fields. Return true is at least one field empty and false if not
function isFieldEmpty() {
    if ($("#molecule-name").val() === "" ||
        $('#sdf-file').get(0).files.length === 0) {
        return true;
    }
    return false;
}