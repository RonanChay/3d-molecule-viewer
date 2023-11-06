$(document).ready(
    function () {
        // Add elements to table
        getElementList();

        // Add onClick event to add element button
        $("#add-element-button").click( () => {
            if (isFieldEmpty() == false) {
                // POST request to add element to database
                $.ajax({
                    url: '/add-element',
                    type: "POST",
                    data: {
                        number: $("#element-number").val(),
                        code: $("#element-code").val(),
                        name: $("#element-name").val(),
                        colour1: $("#element-colour1").val(),
                        colour2: $("#element-colour2").val(),
                        colour3: $("#element-colour3").val(),
                        radius: $("#element-radius").val(),
                    },
                    success: function () {
                        alert("Successfully added element to the database!");
                        getElementList();
                    },
                    error: function () {
                        message = "Failed to add element. Ensure that all the fields are correct.\n\n"
                        message += "Field Restrictions:\n"
                        message += "Element Number: A valid element number between 1 and 118 inclusive\n\n"
                        message += "Element Code: A valid element code/symbol (1 or 2 characters)\n\n"
                        message += "Element Name: A valid element name (only letters)\n\n"
                        message += "Colours 1, 2, 3: A valid colour in hexadecimal\n\n"
                        message += "Radius: A valid radius (integer greater than 0)\n"
                        alert(message)
                    }
                })
            } else {
                alert("There are empty fields! Ensure that all fields are filled in correctly before adding the element")
            }
        })
    }
);

// GET request to get list of elements from database and refresh the elements table
function getElementList() {
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/get-elements",
        success: function (data) {
            refreshElementsTable(JSON.parse(JSON.stringify(data)));
        }
    });
}

// Refresh the elements table with the list of elements from the database
function refreshElementsTable(elements) {
    // Empty current table and append header row
    $("#element-table").empty().append(
        '<tr> <th> Element Number </th> <th> Element Code </th> <th> Element Name </th> <th> Colour 1 </th> <th> Colour 2 </th> <th> Colour 3 </th> <th> Radius </th> <th> Delete Element </th> </tr>'
    )

    // Append all the rows of elements
    for (let i = 0; i < elements.length; i++) {
        var el = elements[i];
        var tableRow = $('<tr>');
        tableRow.attr('id', el.code)
        tableRow.append(
            '<td> ' + el.number + ' </td> <td> ' + el.code + ' </td> <td> ' + el.name + ' </td> <td> #' + el.colour1 + ' </td> <td> #' + el.colour2 + ' </td> <td> #' + el.colour3 + ' </td> <td> ' + el.radius + ' </td> '
        );
        // Delete element button
        var deleteButton = $('<td> <button class="delete-element-button"> Delete </button> </td> </tr>');
        deleteButton.attr(
            'onClick',
            'removeElement(\'' + el.code + '\')'
        )
        
        tableRow.append(deleteButton)
        tableRow.appendTo("#element-table");
    }
}

// POST request to remove element from database
function removeElement(elCode) {
    $.post("/remove-element",
    {
        code: elCode
    },
    function( data, status )
    {
        if (status == "success") {
            var elId = "#" + elCode
            $(elId).remove();
        } else {
            alert("Failed to remove element. Code problem");
        }
    });
}

// Check if there are empty fields. Return true is at least one field empty and false if not 
function isFieldEmpty() {
    if ($("#element-number").val() === "" ||
        $("#element-code").val() === "" ||
        $("#element-name").val() === "" ||
        $("#element-colour1").val() === "" ||
        $("#element-colour2").val() === "" ||
        $("#element-colour3").val() === "" ||
        $("#element-radius").val() === "") {
        
       return true
    }
    return false
}