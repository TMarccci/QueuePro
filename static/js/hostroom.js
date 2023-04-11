// Dark mode switch
const switcher = document.getElementById("darktoggle");
var darkMode = localStorage.getItem('darkMode');

const enableDarkMode = () => {
    // Override the css variables
    document.documentElement.style.setProperty('background-color', '#2a2a2a', 'important');
    document.documentElement.style.setProperty('--bs-body-bg', '#2a2a2a', 'important');
    document.documentElement.style.setProperty('--bs-body-color', '#fff');
    document.documentElement.style.setProperty('text-color', 'white', 'important');
    document.documentElement.style.setProperty('border-color', 'white', 'important');
    // Update darkMode in localStorage
    localStorage.setItem('darkMode', 'enabled');
    // Update the switcher
    switcher.src = "/static/img/sun.png";
}

const disableDarkMode = () => {
    // Override the css variables
    document.documentElement.style.setProperty('background-color', 'white');
    document.documentElement.style.setProperty('--bs-body-bg', '#fff');
    document.documentElement.style.setProperty('--bs-body-color', '#646464');
    document.documentElement.style.setProperty('text-color', 'black');
    document.documentElement.style.setProperty('border-color', 'black');
    // Update darkMode in localStorage
    localStorage.setItem('darkMode', 'disabled');
    // Update the switcher
    switcher.src = "/static/img/moon.png";
}

if (darkMode === 'enabled') {
    enableDarkMode();
}

switcher.addEventListener('click', () => {
    darkMode = localStorage.getItem('darkMode');
  
    if (darkMode !== 'enabled') {
        enableDarkMode();
    }
    else {
        disableDarkMode();
    }
});

// Load next song
function loadNextSong() {
    // Get the next song from the server and load it into the player
    // Get session id
    var sessionid = document.getElementById("sessionidtext").innerText;

    // Make the api call
    $.ajax({
        url: "/hostsession/getnext/" + sessionid,
        type: "POST",
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            // Load the song into the player
            // Parse the data
            console.log(data);

            // Set the player source
            var audiosource = document.getElementById("audiosource");
            audiosource.src = data.directlink;
            // Remove the placeholder-glow and placeholder class from the text and whosent fields
            var infoparent = document.getElementById("titleandmusicserverparent");
            infoparent.classList.remove("placeholder-glow");
            var musictitle = document.getElementById("musictitle");
            musictitle.classList.remove("placeholder");
            var musicserver = document.getElementById("musicserver");
            musicserver.classList.remove("placeholder");
            // Set the text of the title and whosent fields
            musictitle.innerText = data.name;
            musicserver.innerText = data.who_sent;
            // Set the if of the song
            var ifofsong = document.getElementById("idofsong");
            ifofsong.innerText = data.idofsong;
            // Remove the placeholder-glow and placeholder class from the thumbnail
            var albumcoverparent = document.getElementById("albumcoverparent");
            albumcoverparent.classList.remove("placeholder-glow");
            var albumcover = document.getElementById("albumcover");
            albumcover.classList.remove("placeholder");

            // Set the thumbnail
            albumcover.src = data.thumbnailurl;
        }
    });
}

// Move to top
function moveToTop(placeinqueue) {
    // Api call
    data = {
        "placeinqueue": placeinqueue
    };

    // Get session id
    var sessionid = document.getElementById("sessionidtext").innerText;

    // Make the api call
    $.ajax({
        url: "/hostsession/movetotop/" + sessionid,
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            console.log("Moved to top: " + data["success"]);
        }
    });
}

// Delete from queue
function deleteFromQueue(placeinqueue) {
    // Api call
    data = {
        "placeinqueue": placeinqueue
    };

    // Get session id
    var sessionid = document.getElementById("sessionidtext").innerText;

    // Make the api call
    $.ajax({
        url: "/hostsession/deletefromqueue/" + sessionid,
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
            console.log("Deleted from queue: " + data["success"]);
        }
    });
}

// Listen to the streamqueue api channel for the queue of songs
listenAndBuildQueue = function() {
    var session_id = document.getElementById("sessionidtext").innerText;
    var url = 'http://' + window.location.host + '/hostsession/streamqueue/' + session_id;

    if ('EventSource' in window) {
        let source = new EventSource(url)

        source.onmessage = function(event) {
            var data = JSON.parse(event.data);
            console.log(data);

            // There is an another thing that this api can send, which is skip song
            if (data.queue != "skip") {
                // Add the queue items to the queue div (#queueitems)
                var queueitems = document.getElementById("queueitems");
                queueitems.innerHTML = "";

                // Set the text for queue length and total duration (queuetext)
                if (data.queue.length == 0) {
                    document.getElementById("queuetext").innerText = "Queue (Add some music):";
                } else {
                    // Sum the duration of all the songs in the queue
                    var totalduration = 0;
                    for (var i = 0; i < data.queue.length; i++) {
                        totalduration += data.queue[i].videolenght;
                    }

                    // Convert totalduration to hours, minutes and seconds if more than 60 minutes
                    // Should look like this if under 60 minutes: 7:02
                    // Should look like this if over 60 minutes: 1:07:02
                    
                    if (totalduration < 3600) {
                        var hours = 0;
                    } else {
                        var hours = Math.floor(totalduration / 3600);
                        totalduration = totalduration - hours * 3600;
                    }

                    var minutes = Math.floor(totalduration / 60);
                    var seconds = totalduration - minutes * 60;
                    if (seconds < 10) {
                        seconds = "0" + seconds;
                    }

                    if (hours == 0) {
                        document.getElementById("queuetext").innerHTML = "Queue:<br>" + data.queue.length + " songs - " + minutes + ":" + seconds;
                    } else {
                        if (minutes < 10) {
                            minutes = "0" + minutes;
                        }
                        document.getElementById("queuetext").innerHTML = "Queue:<br>" + data.queue.length + " songs - " + hours + ":" + minutes + ":" + seconds;
                    }
                }

                for (var i = 0; i < data.queue.length; i++) {
                    var queueitem = document.createElement("div");
                    queueitem.className = "row mb-3 ms-3 queueitem";
                    queueitem.id = "queueitem" + data.queue[i].placeinqueue;

                    var placeinqueue = data.queue[i].placeinqueue;

                    var col1 = document.createElement("div");
                    col1.className = "col-2 align-self-center";

                    var col1row1 = document.createElement("div");
                    col1row1.className = "row m-0 unselectable";
                    col1row1.style = "height: 50px; width: 50px; border-radius: 10px; background-image: url('" + data.queue[i].thumbnailurl + "'); background-size: cover; background-position: center;";
                    col1.appendChild(col1row1);

                    var col2 = document.createElement("div");
                    col2.className = "col-8";

                    // convert data.queue[i].videolenght to minutes and seconds
                    var minutes = Math.floor(data.queue[i].videolenght / 60);
                    var seconds = data.queue[i].videolenght - minutes * 60;
                    if (seconds < 10) {
                        seconds = "0" + seconds;
                    }
                    
                    var col2row1 = document.createElement("span");
                    col2row1.innerHTML = data.queue[i].name + " - " + minutes + ":" + seconds;
                    col2.appendChild(col2row1);

                    var col2row2 = document.createElement("br");
                    col2.appendChild(col2row2);
                    
                    var col2row3 = document.createElement("span");
                    col2row3.innerText = data.queue[i].sentby;
                    col2.appendChild(col2row3);
                    
                    var col3 = document.createElement("div");
                    col3.className = "col-1 align-self-center";

                    var col3row1 = document.createElement("div");
                    col3row1.className = "row";

                    var col3row1a1 = document.createElement("a");
                    col3row1a1.href = "javascript:moveToTop(" + placeinqueue + ")";

                    var col3row1a1img1 = document.createElement("img");
                    col3row1a1img1.className = "d-block w-100 unselectable imagebutton";
                    col3row1a1img1.src = "/static/img/gototop.png";
                    col3row1a1img1.alt = "Go To Top";
                    col3row1a1.appendChild(col3row1a1img1);

                    col3row1.appendChild(col3row1a1);

                    col3.appendChild(col3row1);

                    var col4 = document.createElement("div");
                    col4.className = "col-1 align-self-center";

                    var col4row1 = document.createElement("div");
                    col4row1.className = "row";

                    var col4row1a1 = document.createElement("a");
                    col4row1a1.href = "javascript:deleteFromQueue(" + placeinqueue + ")";

                    var col4row1a1img1 = document.createElement("img");
                    col4row1a1img1.className = "d-block w-100 unselectable imagebutton";
                    col4row1a1img1.src = "/static/img/delete.png";
                    col4row1a1img1.alt = "Delete";
                    col4row1a1.appendChild(col4row1a1img1);

                    col4row1.appendChild(col4row1a1);

                    col4.appendChild(col4row1);

                    if (placeinqueue == 1) {
                        col3row1.removeChild(col3row1a1);
                    }

                    queueitem.appendChild(col1);
                    queueitem.appendChild(col2);
                    queueitem.appendChild(col3);
                    queueitem.appendChild(col4);

                    queueitems.appendChild(queueitem);
                }
            } else if (data.queue == "skip") {
                loadNextSongThanPlay();
            } else {
                console.log("Somethine went wrong")
            }
        }
      } else {
        console.log('EventSource not supported');
      } 
};

// Setup player
playerSetup = function() {
    const audio = document.getElementById('audiosource');
    const durationContainer = document.getElementById('timeremaining');
    const durationContainerParent = document.getElementById('timeremainingparent');
    const currentTimeContainer = document.getElementById('timecurrent');
    const currentTimeContainerParent = document.getElementById('timecurrentparent');

    // Remove the placeholder-glow and placeholder
    durationContainerParent.classList.remove("placeholder-glow");
    currentTimeContainerParent.classList.remove("placeholder-glow");
    durationContainer.classList.remove("placeholder");
    currentTimeContainer.classList.remove("placeholder");

    const seekSlider = document.getElementById('seek-slider');
    const audioPlayerContainer = document.getElementById('audiosource-container');
    const playIconContainer = document.getElementById('playbutton');
    const volumeSlider = document.getElementById('volume-slider');
    const prevbutton = document.getElementById('prevbutton');
    const nextbutton = document.getElementById('nextbutton');

    let playState = 'play';    

    playIconContainer.addEventListener('click', () => {
        if(playState === 'play') {
            audio.play();
            // Play button to pause button (replace image source)
            playIconContainer.src = "/static/img/pause.png";
            requestAnimationFrame(whilePlaying);
            playState = 'pause';
        } else {
            audio.pause();
            // Pause button to play button (replace image source)
            playIconContainer.src = "/static/img/play.png";
            cancelAnimationFrame(raf);
            playState = 'play';
        }
    });

    const showRangeProgress = (rangeInput) => {
        if(rangeInput === seekSlider) audioPlayerContainer.style.setProperty('--seek-before-width', rangeInput.value / rangeInput.max * 100 + '%');
        else audioPlayerContainer.style.setProperty('--volume-before-width', rangeInput.value / rangeInput.max * 100 + '%');
    }

    prevbutton.addEventListener('click', () => {
        audio.currentTime = 0;
        // Show the current time on the player
        currentTimeContainer.textContent = calculateTime(audio.currentTime);
        // Show the current time on the seek slider
        seekSlider.value = audio.currentTime;
        playIconContainer.src = "/static/img/pause.png";
        requestAnimationFrame(whilePlaying);
        playState = 'pause';
        audio.play();
    });

    nextbutton.addEventListener('click', () => {
        audio.currentTime = audio.duration-0.01;
    });


    seekSlider.addEventListener('input', (e) => {
        showRangeProgress(e.target);
    });
    volumeSlider.addEventListener('input', (e) => {
        showRangeProgress(e.target);
    });

    /** Implementation of the functionality of the audio player */
    const outputContainer = document.getElementById('volvalue');
    let raf = null;

    const calculateTime = (secs) => {
        const minutes = Math.floor(secs / 60);
        const seconds = Math.floor(secs % 60);
        const returnedSeconds = seconds < 10 ? `0${seconds}` : `${seconds}`;
        return `${minutes}:${returnedSeconds}`;
    }

    const displayDuration = () => {
        durationContainer.textContent = calculateTime(audio.duration);
    }

    const setSliderMax = () => {
        seekSlider.max = Math.floor(audio.duration);
    }

    const displayBufferedAmount = () => {
        const bufferedAmount = Math.floor(audio.buffered.end(audio.buffered.length - 1));
        audioPlayerContainer.style.setProperty('--buffered-width', `${(bufferedAmount / seekSlider.max) * 100}%`);
    }

    const whilePlaying = () => {
        seekSlider.value = Math.floor(audio.currentTime);
        currentTimeContainer.textContent = calculateTime(seekSlider.value);
        audioPlayerContainer.style.setProperty('--seek-before-width', `${seekSlider.value / seekSlider.max * 100}%`);
        raf = requestAnimationFrame(whilePlaying);
    }

    if (audio.readyState > 0) {
        displayDuration();
        setSliderMax();
        displayBufferedAmount();
    } else {
        audio.addEventListener('loadedmetadata', () => {
            displayDuration();
            setSliderMax();
            displayBufferedAmount();
        });
    }

    audio.addEventListener('progress', displayBufferedAmount);

    seekSlider.addEventListener('input', () => {
        currentTimeContainer.textContent = calculateTime(seekSlider.value);
        if(!audio.paused) {
            cancelAnimationFrame(raf);
        }
    });

    seekSlider.addEventListener('change', () => {
        audio.currentTime = seekSlider.value;
        if(!audio.paused) {
            requestAnimationFrame(whilePlaying);
        }
    });

    volumeSlider.addEventListener('input', (e) => {
        const value = e.target.value;

        outputContainer.textContent = value;
        audio.volume = value / 100;
    });

    loadNextSongThanPlay = function() {
        // Send to the server that the song has ended
        var idofsong = document.getElementById('idofsong').innerText;
        var sessionid = document.getElementById("sessionidtext").innerText;
        var queuetext = document.getElementById("queuetext")
        // .innerText = "Queue (Add some music):";

        link = "/hostsession/setasplayed/" + sessionid;
        var data = {
            "idInDB": idofsong
        }

        $.ajax({
            type: "POST",
            url: link,
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                if (queuetext.innerText != "Queue (Add some music):") {
                    loadNextSong();

                    // Play button to pause button (replace image source)
                    playIconContainer.src = "/static/img/pause.png";
                    requestAnimationFrame(whilePlaying);
                    playState = 'pause';
                } else {
                    // Pause button to play button (replace image source)
                    playIconContainer.src = "/static/img/play.png";
                    cancelAnimationFrame(raf);
                    playState = 'play';

                    console.log("No more songs in queue");

                    // Put placeholders back
                    var infoparent = document.getElementById("titleandmusicserverparent");
                    infoparent.classList.add("placeholder-glow");
                    var musictitle = document.getElementById("musictitle");
                    musictitle.classList.add("placeholder");
                    var musicserver = document.getElementById("musicserver");
                    musicserver.classList.add("placeholder");
                    // Remove the placeholder-glow and placeholder class from the thumbnail
                    var albumcoverparent = document.getElementById("albumcoverparent");
                    albumcoverparent.classList.add("placeholder-glow");
                    var albumcover = document.getElementById("albumcover");
                    albumcover.classList.add("placeholder");
                    // Albumcover to empty
                    albumcover.src = "/static/img/emptycover.png";
                    // Remove audio source
                    var audiosource = document.getElementById("audiosource");
                    audiosource.src = "";

                    // Set the seek slider to 0
                    seekSlider.value = 0;
                    // Set the current time to 0
                    currentTimeContainer.textContent = calculateTime(0);
                    // Set the duration to 1:00
                    durationContainer.textContent = calculateTime(60);
                }
            },
        });
    }

    document.querySelector("#audiosource").addEventListener("ended", loadNextSongThanPlay, false);

    // Event listener for if the audiosource is playing than the play button should be a pause button and seek slider should be moving and the current time should be updating
    document.querySelector("#audiosource").addEventListener("playing", function() {
        // Play button to pause button (replace image source)
        playIconContainer.src = "/static/img/pause.png";
        requestAnimationFrame(whilePlaying);
        playState = 'pause';
    }, false);
}

listenAndBuildQueue();
playerSetup();
loadNextSong();