$(document).ready(
    function () {
        // GET request to get list of molecules in database and add molecules to sidebar
        $.ajax({
            type: "GET",
            dataType: "json",
            url: "/get-molecules",
            success: function (data) {
                addSidebarMolecules(JSON.parse(JSON.stringify(data)));
            }
        });

        // Rotate button handling
        $("#rotate-button").attr("disabled", true)
        $("#rotate-button").click( () => {
            if (isFieldEmpty() == false) {
                // POST request to rotate molecule and get new svg
                $.ajax( {
                    url: "/rotate-svg",
                    type: "POST",
                    data: {
                            name: $("#molecule-svg-image").attr("value"),
                            xRot: $("#x-value").val(),
                            yRot: $("#y-value").val(),
                            zRot: $("#z-value").val()
                        },
                    success: function( svgContent, status ) {
                            $("#molecule-svg-image").html(svgContent);
                    },
                    error: function() {
                        alert("Rotate failed... Ensure that the pitch/yaw/roll angles are valid (non-negative integers only)");
                    }
                })
            } else {
                alert("There are empty fields! Ensure that all fields are filled in correctly before rotating the molecule")
            }
        })
    }
);


// Creates the molecules list in the sidebar
function addSidebarMolecules(moleculeList) {
    for (let i = 0; i < moleculeList.length; i++) {
        var molData = moleculeList[i];
        var listItem = $(
            '<a class="molecule-list-item"></a>'
        )
        listItem.append(
            '<label class="molecule-name">' + molData.name + ' (' + molData.atomNum + ' atoms, ' + molData.bondNum + ' bonds) </label>'
        ).attr('onClick', "displayMolecule(\'" + molData.name + "\')")
        
        listItem.appendTo("#molecule-list");
    }
}


// POST request to get svg string of molecule and display the svg of the selected molecule
function displayMolecule(molName) {
    $.post("/get-svg",
    {
        name: molName
    },

    function( svgContent, status )
    {
        if (status == "success") {
            $("#molecule-svg-image").html(svgContent);
            $("#molecule-svg-image").attr("value", molName);
            $("#molecule-name").text("Molecule: " + molName)
            $("#rotate-button").attr("disabled", false)
        } else {
            alert("Display failed... Problem with code");
        }
    });
}

// Check if there are empty fields. Return true is at least one field empty and false if not 
function isFieldEmpty() {
    if ($("#x-value").val() === "" ||
        $("#y-value").val() === "" ||
        $("#z-value").val() === "") {
        return true;
    };
    return false;
}
