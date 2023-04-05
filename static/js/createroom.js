/* createSession() function that sends a POST request to the server with the details of the room */
createSession = function() {
    /* Get the values from the form */
    var codefield = document.getElementById("codefield");
    var skipscount = document.getElementById("skipscount");
    var samemusictime = document.getElementById("samemusictime");
    var maxsamesong = document.getElementById("maxsamesong");
    var musiclenght = document.getElementById("musiclenght");

    /* Convert the inner text's to string or int */
    var vskipscount = parseInt(skipscount.innerHTML);
    var vsamemusictime = parseFloat(samemusictime.innerHTML);
    /* Hours Float to seconds */
    var vsamemusictime = vsamemusictime * 60 * 60;
    var vmaxsamesong = parseInt(maxsamesong.innerHTML);
    var vmusiclenght = parseInt(musiclenght.innerHTML);
    /* Minutes to seconds */
    var vmusiclenght = vmusiclenght * 60;

    /* Create the data to send */
    var data = {
        "code": codefield.value,
        "skips": vskipscount,
        "samemusictime": vsamemusictime,
        "maxsamesong": vmaxsamesong,
        "maxvideolenght": vmusiclenght
    };

    /* Send the data in json to the server: application/json */
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/registerhostsession",
        data: JSON.stringify(data),
        success: function(data) {
            /* Redirect to the room, the response continas the roomid */
            /* Define room id */
            var roomid = data.roomid;
            /* Redirect to the room */
            window.location.href = "/hostsession/" + roomid;
        },
        error: function(data) {
            /* Show error by removing d-none and unselectable class id: errormessagecreation */
            var errormessagecreation = document.getElementById("errormessagecreation");
            errormessagecreation.classList.remove("d-none");
            errormessagecreation.classList.remove("unselectable");

            console.log(data);
        }
    });
}

/* decrementSkips() Decrement skips / people 's count id: skipscount */
decrementSkips = function() {
    var skipscount = document.getElementById("skipscount");
    if (skipscount.innerHTML > 0) {
        /* Decrement the count */
        skipscount.innerHTML = parseInt(skipscount.innerHTML) - 1;
    } else {
        /* Do nothing */
    }
}

/* incrementSkips() Increment skips / people 's count id: skipscount */
incrementSkips = function() {
    var skipscount = document.getElementById("skipscount");
    if (skipscount.innerHTML < 20) {
        /* Increment the count */
        skipscount.innerHTML = parseInt(skipscount.innerHTML) + 1;
    } else {
        /* Do nothing */
    }
}

/* decrementTimeBetweenSame() Decrement time between same / time 's count id: samemusictime */
decrementTimeBetweenSame = function() {
    var samemusictime = document.getElementById("samemusictime");
    /* Decrement the count by 0,5 until max 0,5 h */
    /* Max 10 h */

    if (samemusictime.innerHTML > 0.5) {
        samemusictime.innerHTML = parseFloat(samemusictime.innerHTML) - 0.5;
    } else {
        /* Do nothing */
    }
}

/* incrementTimeBetweenSame() Increment time between same / time 's count id: samemusictime */
incrementTimeBetweenSame = function() {
    var samemusictime = document.getElementById("samemusictime");
    /* Increment the count by 0,5 until max 10 h */
    if (samemusictime.innerHTML < 10) {
        samemusictime.innerHTML = parseFloat(samemusictime.innerHTML) + 0.5;
    } else {
        /* Do nothing */
    }
}

/* decrementMaxOfSameSong() Decrement max of same song / max 's count id: maxsamesong */
decrementMaxOfSameSong = function() {
    var maxsamesong = document.getElementById("maxsamesong");
    /* Decrement the count by 1 until max 1 */
    if (maxsamesong.innerHTML > 1) {
        maxsamesong.innerHTML = parseInt(maxsamesong.innerHTML) - 1;
    } else {
        /* Do nothing */
    }
}

/* incrementMaxOfSameSong() Increment max of same song / max 's count id: maxsamesong */
incrementMaxOfSameSong = function() {
    var maxsamesong = document.getElementById("maxsamesong");
    /* Increment the count by 1 until max 20 */
    if (maxsamesong.innerHTML < 20) {
        maxsamesong.innerHTML = parseInt(maxsamesong.innerHTML) + 1;
    } else {
        /* Do nothing */
    }
}

/* decrementMaxLenghtSong() Decrement max of same song / max 's count id: musiclenght */
decrementMaxLenghtSong = function() {
    var musiclenght = document.getElementById("musiclenght");
    /* Decrement the count by 1 until max 1 */
    if (musiclenght.innerHTML > 1) {
        musiclenght.innerHTML = parseInt(musiclenght.innerHTML) - 1;
    } else {
        /* Do nothing */
    }
}

/* incrementMaxLenghtSong() Increment max of same song / max 's count id: musiclenght */
incrementMaxLenghtSong = function() {
    var musiclenght = document.getElementById("musiclenght");
    /* Increment the count by 1 until max 30 */
    if (musiclenght.innerHTML < 30) {
        musiclenght.innerHTML = parseInt(musiclenght.innerHTML) + 1;
    } else {
        /* Do nothing */
    }
}

/* validAndCreateSession() Check if there is room code id: codefield */
validAndCreateSession = function() {
    var codefield = document.getElementById("codefield");
    if (codefield.value.length > 5) {
        /* Remove error by adding d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.add("d-none");
        errormessage.classList.add("unselectable");

        /* Create the session */
        createSession();
    } else {
        /* Show error by removing d-none and unselectable class id: errormessage */
        var errormessage = document.getElementById("errormessage");
        errormessage.classList.remove("d-none");
        errormessage.classList.remove("unselectable");

        /* Do nothing */
    }
}