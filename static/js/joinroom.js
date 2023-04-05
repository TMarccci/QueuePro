/* validAndJoinSession() Check if there is room code id: codefield */
validAndJoinSession = function() {
    var codefield = document.getElementById("codefield");
    var errormessageonnotenoughcharacters = "Fill the code field! <br>(Min. 6 characters)"
    var nosessionwithcode = "No session with this code! <br>(Check the code)"
    var alerttextcontent = document.getElementById("alerttext");

    if (codefield.value.length > 5) {
        /* Remove error by adding d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.add("d-none");
        errormessage.classList.add("unselectable");

        /* Join the session */
        /* Get the values from the form */
        var codefield = document.getElementById("codefield");

        /* Create the data to send */
        var data = {
            "code": codefield.value,
        };

        /* Send the data in json to the server: application/json */
        $.ajax({
            type: "POST",
            contentType: "application/json",
            url: "/joinsessionapi",
            data: JSON.stringify(data),
            success: function(data) {
                /* Redirect to the room, the response continas the roomid */
                /* Define room id */
                var response = data.response;

                if (data.response == "Session not found") {
                    /* Show error by removing d-none and unselectable class id: errormessagejoin */
                    var errormessage = document.getElementById("errormessage");
                    // set the alert text content
                    alerttextcontent.innerHTML = nosessionwithcode;
                    // remove the hider class
                    errormessage.classList.remove("d-none");
                    errormessage.classList.remove("unselectable");
                }
                else {
                    var roomid = data.response;

                    /* Redirect to the room */
                    window.location.href = "/joinsession/" + roomid;
                }
            },
            error: function(data) {
                /* Show error by removing d-none and unselectable class id: errormessagejoin */
                var errormessagecreation = document.getElementById("errormessagecreation");
                errormessagecreation.classList.remove("d-none");
                errormessagecreation.classList.remove("unselectable");
            }
        });


    } else {
        // set the alert text content
        alerttextcontent.innerHTML = errormessageonnotenoughcharacters;

        /* Show error by removing d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.remove("d-none");
        errormessage.classList.remove("unselectable");
    }
}