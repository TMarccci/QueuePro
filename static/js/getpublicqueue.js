// Listen to the streamqueue api channel
// This is used to update the queue in real time and sometimes it contains the details to skip song
listenAndBuildQueueForPublic = function() {
    var session_id = document.getElementById("sessionidtext").innerText;
    var url = 'https://' + window.location.host + '/hostsession/streamqueue/' + session_id;


    if ('EventSource' in window) {
        let source = new EventSource(url)

        source.onmessage = function(event) {
            var data = JSON.parse(event.data);
            console.log(data);

            // There is an another thing that this api can send, which is skip song
            // Add the queue items to the queue div (#queueitems)
            var queueitems = document.getElementById("queueitems");
            queueitems.innerHTML = "";

            // Set the text for queue length and total duration (queuetext)
            if (data.queue.length == 0) {
                document.getElementById("queuetext").innerText = "Queue:";
                localStorage.setItem('queueitemscount', 0);
                var queuetextplace = document.getElementById("queueitems");
                var alertmsg  = "<h4 class=\"text-center lead\">The queue is empty!<br>Go and fill it fast!</h4>";
                queuetextplace.innerHTML = alertmsg;
            } else {
                var queuetextplace = document.getElementById("queueitems");
                queuetextplace.innerHTML = "";

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

                for (var i = 0; i < data.queue.length; i++) {
                    var queueitem = document.createElement("div");
                    queueitem.className = "row mb-3 ms-3 queueitem";
                    queueitem.id = "queueitem" + data.queue[i].placeinqueue;

                    var placeinqueue = data.queue[i].placeinqueue;

                    var col1 = document.createElement("div");
                    col1.className = "col-2 align-self-center text-center";

                    var col1row1 = document.createElement("div");
                    col1row1.className = "row m-0 unselectable";
                    col1row1.style = "height: 50px; width: 50px; border-radius: 10px; background-image: url('" + data.queue[i].thumbnailurl + "'); background-size: cover; background-position: center;";
                    col1.appendChild(col1row1);

                    var col2 = document.createElement("div");
                    col2.className = "col-10";

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

                    queueitem.appendChild(col1);
                    queueitem.appendChild(col2);

                    queueitems.appendChild(queueitem);
                }

                localStorage.setItem('queueitemscount', data.queue.length);
            }
        }
      } else {
        console.log('EventSource not supported');
      } 
};

listenAndBuildQueueForPublic();