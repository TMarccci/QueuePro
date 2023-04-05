// validateAndSendLink() is called when the user clicks the "Send" button
validateAndSendLink = function() {
    var linkfield = document.getElementById("linkfield");
    var link = linkfield.value;
    var sessionid = document.getElementById("sessionidtext").innerText;
    var userid = document.getElementById("useridtext").innerText;
    var combinedurl = "/managesessionapi/" + sessionid + "/" + userid;

    isvalid = validateYouTubeUrl(link);

    if (isvalid) {
        // Api responses to handle:
        /*
        resonses = {
            'response': "Link added to the queue",
            'response': "Song already played in the last " + str(timebetweensamemusic) + " seconds",
            'response': "Song already played more than " + str(samemusicmaxtimes) + " times"
        }*/

        // hide the error
        var errormessage = document.getElementById("errormessage");
        // add the hider class
        errormessage.classList.add("d-none");
        errormessage.classList.add("unselectable");

        // hide the error
        var errormessagesend = document.getElementById("errormessagesend");
        // add the hider class
        errormessagesend.classList.add("d-none");
        errormessagesend.classList.add("unselectable");

        // send the link to the server
        var data = {
            'link': link,
            'sessionid': sessionid,
            'guestid': userid
        };

        $.ajax({
            type: "POST",
            contentType: "application/json",
            url: combinedurl,
            data: JSON.stringify(data),
            dataType: 'json',
            cache: false,
            timeout: 600000,
            success: function(data) {
                // If "Link added to the queue" is returned, clear the link field
                if (data.response == "Link added to the queue") {
                    linkfield.value = "";
                } else {
                    // set the alert text content
                    var alerttextcontent = document.getElementById("alerttext");
                    alerttextcontent.innerHTML = data.response;

                    /* Show error by removing d-none and unselectable class id: errormessage */
                    var errormessage = document.getElementById("errormessage");
                    errormessage.classList.remove("d-none");
                    errormessage.classList.remove("unselectable");
                }
            },
            error: function(e) {
                // Show error by removing d-none and unselectable class id: errormessagesend
                var errormessagesend = document.getElementById("errormessagesend");
                errormessagesend.classList.remove("d-none");
                errormessagesend.classList.remove("unselectable");
            }
        });
    } else {
        // set the alert text content
        var alerttextcontent = document.getElementById("alerttext");
        alerttextcontent.innerHTML = "Invalid link! <br>Try again!";

        /* Show error by removing d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.remove("d-none");
        errormessage.classList.remove("unselectable");
    }
}

// validateYouTubeUrl() is called when the user clicks the "Send" button
function validateYouTubeUrl(link)
{
    var url = link;
        if (url != undefined || url != '') {
            var regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=|\?v=)([^#\&\?]*).*/;
            var match = url.match(regExp);
            if (match && match[2].length == 11) {
                return true;
            }
            else {
                return false;
            }
        }
}

// Clipboard API
if (navigator.clipboard) {
    console.log('Clipboard API available');
}

var pasteButton = document.getElementById("pastebtn");

pasteButton.addEventListener('click', async () => {
    var linkfield = document.getElementById("linkfield");
    const text = await navigator.clipboard.readText()
    linkfield.value = text;
})