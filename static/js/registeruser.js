// sendNameAndJoinSession() is called when the user clicks the "Join" button
sendNameAndJoinSession = function() {
    var namefield = document.getElementById("namefield");

    if (namefield.value.length > 2) {
        /* Remove error by adding d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.add("d-none");
        errormessage.classList.add("unselectable");

        /* Join the session */
        /* Get the values from the form */
        var namefield = document.getElementById("namefield");
        var sessionid = document.getElementById("sessionidtext");

        /* Create the data to send */
        var data = {
            "name": namefield.value,
            "sessionid": sessionid.innerText,
        };

        var combinedurl = "/joinsessionapi/" + sessionid.innerText;

        /* Send the data in json to the server: application/json */
        $.ajax({
            type: "POST",
            contentType: "application/json",
            url: combinedurl,
            data: JSON.stringify(data),
            success: function(data) {
                /* Redirect to the room, the response continas the roomid */
                /* Define room id */

                if (data.response == "Error getting skipsleft") {
                    // set the alert text content
                    var alerttextcontent = document.getElementById("alerttext");
                    alerttextcontent.innerHTML = "Error Getting Skipsleft!<br>Try again!<br>Possible internal server error!";

                    /* Show error by removing d-none and unselectable class id: errormessage */
                    var errormessage = document.getElementById("errormessage");
                    errormessage.classList.remove("d-none");
                    errormessage.classList.remove("unselectable");
                }

                else if (data.response == "Name already taken") {
                    // set the alert text content
                    var alerttextcontent = document.getElementById("alerttext");
                    alerttextcontent.innerHTML = "Name already taken!<br>Try another one!";

                    /* Show error by removing d-none and unselectable class id: errormessage */
                    var errormessage = document.getElementById("errormessage");
                    errormessage.classList.remove("d-none");
                    errormessage.classList.remove("unselectable");
                }

                else {
                    var guestid = data.response;
                    // hide the error
                    var errormessage = document.getElementById("errormessage");
                    // add the hider class
                    errormessage.classList.add("d-none");
                    errormessage.classList.add("unselectable");

                    /* Redirect to the room */
                    window.location.href = "/managesession/" + sessionid.innerText + "/" + guestid;
                }
            },
            error: function(data) {
                /* Show error by removing d-none and unselectable class id: errormessagejoin */
                var errormessagecreation = document.getElementById("errormessagejoin");
                errormessagecreation.classList.remove("d-none");
                errormessagecreation.classList.remove("unselectable");
            }
        });


    } else {
        // set the alert text content
        var alerttextcontent = document.getElementById("alerttext");
        alerttextcontent.innerHTML = "Username not long enough!<br>(Min. 3 characters)";

        /* Show error by removing d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.remove("d-none");
        errormessage.classList.remove("unselectable");
    }
}