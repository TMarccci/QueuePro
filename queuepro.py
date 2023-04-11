from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify, send_file, send_from_directory
import mysql.connector, uuid, time, segno, datetime, json, mysql.connector.pooling
from pytube import YouTube 

hostIp = '192.168.0.27'
domain = 'https://queuepro.tmarccci.hu'
hostPort = 5000
app = Flask(__name__)

host = '192.168.0.27'
user = 'pythonuser'
password = 'nn253g8v@'
database = 'queuepro'

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=15, host=host, user=user, password=password, database=database)

@app.route('/')
def index():
    return render_template('home.html', title="QueuePro - Home")

# Host session page, the user can create room here
@app.route('/hostsession')
def hostsession():
    return render_template('createsession.html', title="QueuePro - Create Music Session")

# Register host session to database API Segment
@app.route('/registerhostsession', methods=['POST'])
def registerhostsession():
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "code": codefield.value,
        #    "skips": skipscount.innerHTML,
        #    "samemusictime": samemusictime.innerHTML,
        #    "maxsamesong": maxsamesong.innerHTML,
        #    "maxvideolenght": maxvideolenght.innerHTML
        # };

        data = request.json

        # Session code, this is custom
        sessioncode = data['code']
        # Skips per user, this is custom
        skipsperuser = data['skips']
        # Time between same music, this is custom (seconds)
        timebetweensamemusic = data['samemusictime']
        # Same music max times, this is custom
        samemusicmaxtimes = data['maxsamesong']
        # Max video lenght, this is custom (seconds)
        maxvideolenght = data['maxvideolenght']
        # Session id, this is generated
        sessionid = str(uuid.uuid4())
        # Datetime, this is generated
        creationdate = time.strftime('%Y-%m-%d %H:%M:%S')

        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "INSERT INTO qp_sessions (sessionid, sessioncode, skipsperuser, timebetweensamemusic, samemusicmaxtimes, 	maxvideolenght, creationdate, skipcurrent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (sessionid, sessioncode, skipsperuser, timebetweensamemusic, samemusicmaxtimes, maxvideolenght, creationdate, 0)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        # Generate QR code for session
        generate_qr_code(sessionid)

        # Return room's session id to make it reachable: data.roomid in javascript
        return jsonify({'roomid': sessionid})

@app.route('/hostsession/<sessionid>')
def hostsessionid(sessionid):
    return render_template('hostsession.html', sessionid=sessionid, title="QueuePro - Host Session")

# Generate QR code for session
def generate_qr_code(sessionid):
    link = f'{domain}/joinsession/{sessionid}'

    qr = segno.make_qr(link)
    qr.save(f'static/qrs/{sessionid}.png', scale=10)

# Serve QR code for session
@app.route('/serverqr/<sessionid>', methods=['GET'])
def serverqr(sessionid):
    return send_from_directory('static/qrs', f'{sessionid}.png')

# Stream the queue to the host
@app.route('/hostsession/streamqueue/<sessionid>')
def streamqueue(sessionid):
    def get_data():
        data = get_queue_andifskip(sessionid)
        
        while True:
            # Check if the queue has been modified
            current_queue = get_queue_andifskip(sessionid)
            if current_queue != data['queue']:
                data['queue'] = current_queue
                yield "data: {}\n\n".format(json.dumps(data['queue'])).encode('utf-8')

            for x in range(200):
                time.sleep(0.01)


    return Response(get_data(), mimetype='text/event-stream')

# Get the queue from the database
def get_queue_andifskip(sessionid):
    # Check the qp_sessions for if someone requested a skip
    cnx = cnxpool.get_connection()
    mycursor = cnx.cursor()
    sql = "SELECT skipcurrent FROM qp_sessions WHERE sessionid = %s"
    val = (sessionid,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    cnx.close()

    skipcurrent = myresult[0][0]

    if skipcurrent != 1:
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT * FROM qp_sessionmusics WHERE whichsession = %s AND isplayed = 0 AND placeinqueue > 0 ORDER BY placeinqueue ASC"
        val = (sessionid,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()
        
        data = {
            'queue': []
        }
        
        for x in myresult:
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            # Get who sent
            sql = "SELECT username FROM qp_sessionusers WHERE userid = %s"
            # whichsession userid username skipsleft totalsongs
            val = (x[2],)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()
            
            # Who sent
            username = myresult[0][0]
            
            # Get video info
            name = x[8]
            
            # Get video thumbnail
            thumbnailurl = x[10]
            
            # Get video lenght
            lenght = x[9]
            
            # Get place in queue
            placeinqueue = x[4]
            
            # Append to data
            data['queue'].append({
                'name': name,
                'sentby': username,
                'placeinqueue': placeinqueue,
                'thumbnailurl': thumbnailurl,
                'videolenght': lenght,
            })

        return data
    else:
        # Set skipcurrent to 0
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "UPDATE qp_sessions SET skipcurrent = 0 WHERE sessionid = %s"
        val = (sessionid,)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        data = {
            'queue': 'skip'
        }

        return data

# Move to the top of the queue api
@app.route('/hostsession/movetotop/<sessionid>', methods=['POST'])
def movetotop(sessionid):
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "placeinqueue": placeinqueue.innerHTML
        # };

        data = request.json

        # Place in queue
        placeinqueue = data['placeinqueue']

        # The move to top function works like this
        # eg. you get placeinqueue = 3
        # 1. Get the id of the placeinqueue = 3
        # 2. Add 1 to all the placeinqueue's
        # 3. Set the placeinqueue of the id to 1

        # Get the id of the placeinqueue = 3
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND placeinqueue = %s"
        val = (sessionid, placeinqueue)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        # Get the id
        id = myresult[0][0]

        # Add 1 to placeinqueue for the songs is are above the song
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "UPDATE qp_sessionmusics SET placeinqueue = placeinqueue + 1 WHERE whichsession = %s AND placeinqueue < %s AND isplayed = 0 AND isplaying = 0"
        val = (sessionid, placeinqueue)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        # Set the placeinqueue of the id to 1
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "UPDATE qp_sessionmusics SET placeinqueue = 1 WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        # Return
        return jsonify({'success': True})

# Delete from queue api
@app.route('/hostsession/deletefromqueue/<sessionid>', methods=['POST'])
def deletefromqueue(sessionid):
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "placeinqueue": placeinqueue.innerHTML
        # };

        data = request.json

        # Place in queue
        placeinqueue = data['placeinqueue']

        # Get the id of the placeinqueue
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND placeinqueue = %s"
        val = (sessionid, placeinqueue)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        # Get the id
        id = myresult[0][0]

        # Reduce all the placeinqueue's by 1 after the deleted one
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "UPDATE qp_sessionmusics SET placeinqueue = placeinqueue - 1 WHERE whichsession = %s AND placeinqueue > %s"
        val = (sessionid, placeinqueue)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        # Delete the song from the queue
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "DELETE FROM qp_sessionmusics WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()


        # Return
        return jsonify({'success': True})

# Direct link provider api for the host
@app.route('/hostsession/directlink/<sessionid>', methods=['POST'])
def directlink(sessionid):
    if request.method == 'POST':
        data = request.json

        link = data['link']
        video = YouTube(link)

        direct_link = video.streams.filter(only_audio=True).first().url

        # Return
        return jsonify({'directlink': direct_link})

# Get next of the queue api
@app.route('/hostsession/getnext/<sessionid>', methods=['POST'])
def getnext(sessionid):
    # This function should work like
    # Get the next song in the queue of the session
    # Set the song to isplaying = 1
    # If in the session there's the next song is isplaying = 1 then send it again because maybe something went wrong so continue
    
    if request.method == 'POST':
        # Check for is there a song in the queue that is isplaying = 1
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT * FROM qp_sessionmusics WHERE whichsession = %s AND isplaying = 1"
        val = (sessionid,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        # If there's a song that is isplaying = 1 then send it again
        if len(myresult) != 0:
            # Get the song details (directlink, name, thumbnailurl, who sent it, idofsong)
            url = myresult[0][3]
            name = myresult[0][8]
            thumbnailurl = myresult[0][10]
            idofsong = myresult[0][0]

            # Get the direct link
            video = YouTube(url)
            directlink = video.streams.filter(only_audio=True).first().url

            # Get the user who sent it
            who_sent = myresult[0][2]
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT username FROM qp_sessionusers WHERE userid = %s"
            val = (who_sent,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            who_sent = myresult[0][0]

            # Return
            return jsonify({'directlink': directlink, 'name': name, 'thumbnailurl': thumbnailurl, 'who_sent': who_sent, 'idofsong': idofsong})
        else:
            # Get the next song in the queue
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT * FROM qp_sessionmusics WHERE whichsession = %s AND isplayed = 0 ORDER BY placeinqueue ASC LIMIT 1"
            val = (sessionid,)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            idofnext = myresult[0][0]

            # If there's a song in the queue then send it
            if len(myresult) != 0:
                # Set the song to isplaying = 1
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "UPDATE qp_sessionmusics SET isplaying = 1 WHERE whichsession = %s AND isplayed = 0 ORDER BY placeinqueue ASC LIMIT 1"
                val = (sessionid,)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()

                # Get the song details (directlink, name, thumbnailurl, who sent it, idofsong)
                url = myresult[0][3]
                name = myresult[0][8]
                thumbnailurl = myresult[0][10]
                idofsong = myresult[0][0]

                # Get the direct link
                video = YouTube(url)
                directlink = video.streams.filter(only_audio=True).first().url

                # Get the user who sent it
                who_sent = myresult[0][2]
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "SELECT username FROM qp_sessionusers WHERE userid = %s"
                val = (who_sent,)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                cnx.close()

                who_sent = myresult[0][0]

                # Set the placeinqueue of the songs after the played one to -1
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "UPDATE qp_sessionmusics SET placeinqueue = placeinqueue - 1 WHERE whichsession = %s AND placeinqueue > (SELECT placeinqueue FROM qp_sessionmusics WHERE id = %s)"
                val = (sessionid, idofnext,)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()

                # Set the placeinqueue of the played song to -1
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "UPDATE qp_sessionmusics SET placeinqueue = -1 WHERE whichsession = %s AND id = %s"
                val = (sessionid, idofnext,)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()

                # Return
                return jsonify({'directlink': directlink, 'name': name, 'thumbnailurl': thumbnailurl, 'who_sent': who_sent, 'idofsong': idofsong})

# Set as played api
@app.route('/hostsession/setasplayed/<sessionid>', methods=['POST'])
def setasplayed(sessionid):
    if request.method == 'POST':
        '''
            {
            "idInDB": 87
            }
        '''
        data = request.json
        # Get the song that is finished playing id
        # Set the song to isplaying = 0
        # Set the song to isplayed = 1
        # Set the song ifplayedwhen to current time

        id = data['idInDB']
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "UPDATE qp_sessionmusics SET isplaying = 0, isplayed = 1, ifplayedwhen = %s WHERE id = %s"
        val = (datetime.datetime.now(), id)
        mycursor.execute(sql, val)
        cnx.commit()
        cnx.close()

        # Return
        return jsonify({'success': True})

# Join session page, the user can enter join code here
@app.route('/joinsession')
def joinsession():
    return render_template('joinsession.html', title="QueuePro - Join Session")

# Join session api to server session id by join code
@app.route('/joinsessionapi', methods=['POST'])
def joinsessionapi():
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "code": codefield.value
        # };

        data = request.json

        # Join code, this is custom
        joincode = data['code']

        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT sessionid FROM qp_sessions WHERE sessioncode = %s"
        val = (joincode,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        if len(myresult) == 0:
            return jsonify({'response': 'Session not found'})
        else:
            return jsonify({'response': myresult[0][0]})

# Join session page, the user can enter his name here (also this is where the user dropped with qr code)
@app.route('/joinsession/<sessionid>')
def joinsessionid(sessionid):
    return render_template('managesessionguest.html', sessionid=sessionid, title="QueuePro - Join Session")

# Join session api to server session register the user
@app.route('/joinsessionapi/<sessionid>', methods=['POST'])
def joinsessionapiid(sessionid):
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "name": namefield.value,
        #    "sessionid": sessionid
        # };

        data = request.json

        # Session id
        sessionidfromapi = data['sessionid']
        # Guest id
        guestid = str(uuid.uuid4())
        # Guest name
        guestname = data['name']
        # Totalsongs default for user is 0
        totalsongs = 0
        try:
            # Get default preferences from the session (skipsleft)
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT skipsperuser FROM qp_sessions WHERE sessionid = %s"
            val = (sessionidfromapi,)
            mycursor.execute(sql, val)
            preferenceresult = mycursor.fetchall()

            skipsleft = preferenceresult[0][0]
        except:
            skipsleft = "Error getting skipsleft"
            print("Error getting skipsleft2")

        if skipsleft == "Error getting skipsleft":
            print("Error getting skipsleft")
            return jsonify({'response': 'Error getting skipsleft'})
        else:
            # Check if there are already a user with the same name in the session
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT username FROM qp_sessionusers WHERE whichsession = %s AND username = %s"
            val = (sessionidfromapi, guestname)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            if len(myresult) != 0:
                return jsonify({'response': "Name already taken"})
            else:
                # Table cols: whichsession	userid	username	skipsleft	totalsongs
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "INSERT INTO qp_sessionusers (whichsession, userid, username, skipsleft, totalsongs) VALUES (%s, %s, %s, %s, %s)"
                val = (sessionidfromapi, guestid, guestname, skipsleft, totalsongs)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()
                return jsonify({'response': guestid})

# Control session page, the user can control the session here
@app.route('/managesession/<sessionid>/<guestid>')
def managesessionid(sessionid, guestid):
    # Get the users remaining skips
    cnx = cnxpool.get_connection()
    mycursor = cnx.cursor()
    sql = "SELECT skipsleft FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
    val = (sessionid, guestid)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    cnx.close()

    skipsleft = myresult[0][0]

    return render_template('managesession.html', sessionid=sessionid, guestid=guestid, skipsleft=skipsleft, title="QueuePro - Session")

# Control session api to server register links and check
@app.route('/managesessionapi/<sessionid>/<guestid>', methods=['POST'])
def managesessionapiid(sessionid, guestid):
    if request.method == 'POST':
        # Payload data
        # data = {
        #    "link": linkfield.value,
        #    "sessionid": sessionid,
        #    "guestid": guestid
        # };

        data = request.json

        # Session id
        sessionidfromapi = data['sessionid']
        # Guest id
        guestidfromapi = data['guestid']
        # Link
        link = data['link']

        # Database (qp_sessionmusics):
        # 	id     whichsession    sentbywhoid url placeinqueue  isplaying  isplayed    ifplayedwhen(datetime)    videoname   videolenght     thumbnailurl
        # Response:
        # -"Song already played in the last " + str(timebetweensamemusic/60/60) + " hours"
        # -"Song already played more than " + str(samemusicmaxtimes) + " times"
        # -"Link added to the queue"
        # -"Song is already in the queue but not played yet"
        yt = YouTube(link)

        # Replace schematic link
        link = yt.watch_url

        # Get video name
        videoname = yt.title

        # Get video lenght
        videolenght = yt.length

        # Get thumbnail url
        thumbnailurl = yt.thumbnail_url

        # Get time between songs
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT timebetweensamemusic FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        timebetweensamemusic = mycursor.fetchall()
        cnx.close()

        # Get max times a song can be played
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT samemusicmaxtimes FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        samemusicmaxtimes = mycursor.fetchall()
        cnx.close()

        # Get max video lenght preference
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT maxvideolenght FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        maxvideolenght = mycursor.fetchall()
        cnx.close()

        # 1. Check that is it in the queue already

        #   - If no then check if the video is longer than the max video lenght preference
        #    - If no then add it to the queue
        #       - Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
        #    - If yes then return "Video is longer than the max video lenght preference"

        #   - If yes then check if it is played
        #    - If no then return "Song is already in the queue but not played yet"
        #    - If yes then check if it is playeable again (samemusicmaxtimes)
        #     - If no then return "Song already played more than " + str(samemusicmaxtimes) + " times"
        #     - If yes then check if it is played in the last x time (timebetweensamemusic)
        #      - If no then check it that is it in the queue already waiting to be played

        #       - If no then check if the video is longer than the max video lenght preference
        #        - If no then add it to the queue
        #           - Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
        #        - If yes then return "Video is longer than the max video lenght preference"

        #       - If yes then return "Song is already in the queue but not played yet"
        #      - If yes then return "Song already played in the last " + str(timebetweensamemusic/60/60) + " hours"

        # Check if the song is already in the queue
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s"
        val = (sessionidfromapi, link)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        if len(myresult) == 0:
            # If no then check if the video is longer than the max video lenght preference
            if videolenght <= maxvideolenght[0][0]:
                # If no then add it to the queue
                # Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "SELECT placeinqueue FROM qp_sessionmusics WHERE whichsession = %s AND placeinqueue > 0 AND isplayed = 0 AND isplaying = 0 ORDER BY placeinqueue DESC"
                val = (sessionidfromapi,)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                cnx.close()

                if len(myresult) == 0:
                    placeinqueue = 1
                else:
                    placeinqueue = myresult[0][0] + 1

                # Add to the queue
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "INSERT INTO qp_sessionmusics (whichsession, sentbywhoid, url, placeinqueue, isplaying, isplayed, ifplayedwhen, videoname, videolenght, thumbnailurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (sessionidfromapi, guestidfromapi, link, placeinqueue, 0, 0, 0, videoname, videolenght, thumbnailurl)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()

                # Add total songs +1 to the users stat
                # qp_sessionusers -> the sessions current users totalsongs
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "SELECT totalsongs FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
                val = (sessionidfromapi, guestidfromapi)
                mycursor.execute(sql, val)
                totalsongs = mycursor.fetchall()
                cnx.close()

                totalsongs = totalsongs[0][0] + 1
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "UPDATE qp_sessionusers SET totalsongs = %s WHERE whichsession = %s AND userid = %s"
                val = (totalsongs, sessionidfromapi, guestidfromapi)
                mycursor.execute(sql, val)
                cnx.commit()
                cnx.close()

                return jsonify({'response': "Link added to the queue"}) 
            else:
                # If yes then return "Video is longer than the max video lenght preference"
                return jsonify({'response': "Video is longer than the max video lenght preference!"})
        else:
            # If yes then check if it is on the queue and not played
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT isplayed FROM qp_sessionmusics WHERE whichsession = %s AND url = %s"
            val = (sessionidfromapi, link)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            if myresult[0][0] == 0:
                # If no then return "Song is already in the queue but not played yet"
                return jsonify({'response': "Song is already in the queue but not played yet!"})
            else:
                # If yes then check if it is playeable again (samemusicmaxtimes)
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 0"
                val = (sessionidfromapi, link)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                cnx.close()

                if len(myresult) < samemusicmaxtimes[0][0]-1:
                    # If yes then check if it is played in the last x time (timebetweensamemusic)
                    cnx = cnxpool.get_connection()
                    mycursor = cnx.cursor()
                    sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 1 AND ifplayedwhen > %s"
                    val = (sessionidfromapi, link, datetime.datetime.now() - datetime.timedelta(seconds=timebetweensamemusic[0][0]))
                    mycursor.execute(sql, val)
                    myresult = mycursor.fetchall()
                    cnx.close()

                    if len(myresult) == 0:
                        # If no then check it that is it in the queue already waiting to be played
                        cnx = cnxpool.get_connection()
                        mycursor = cnx.cursor()
                        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 0"
                        val = (sessionidfromapi, link)
                        mycursor.execute(sql, val)
                        myresult = mycursor.fetchall()
                        cnx.close()

                        if len(myresult) == 0:
                            # If no then check if the video is longer than the max video lenght preference
                            if videolenght <= maxvideolenght[0][0]:
                                # If no then add it to the queue
                                # Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
                                cnx = cnxpool.get_connection()
                                mycursor = cnx.cursor()
                                sql = "SELECT placeinqueue FROM qp_sessionmusics WHERE whichsession = %s AND placeinqueue > 0 AND isplayed = 0 AND isplaying = 0 ORDER BY placeinqueue DESC"
                                val = (sessionidfromapi,)
                                mycursor.execute(sql, val)
                                myresult = mycursor.fetchall()
                                cnx.close()

                                if len(myresult) == 0:
                                    placeinqueue = 1
                                else:
                                    placeinqueue = myresult[0][0] + 1

                                # Add to the queue
                                cnx = cnxpool.get_connection()
                                mycursor = cnx.cursor()
                                sql = "INSERT INTO qp_sessionmusics (whichsession, sentbywhoid, url, placeinqueue, isplaying, isplayed, ifplayedwhen, videoname, videolenght, thumbnailurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                val = (sessionidfromapi, guestidfromapi, link, placeinqueue, 0, 0, 0, videoname, videolenght, thumbnailurl)
                                mycursor.execute(sql, val)
                                cnx.commit()
                                cnx.close()

                                # Add total songs +1 to the users stat
                                # qp_sessionusers -> the sessions current users totalsongs
                                cnx = cnxpool.get_connection()
                                mycursor = cnx.cursor()
                                sql = "SELECT totalsongs FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
                                val = (sessionidfromapi, guestidfromapi)
                                mycursor.execute(sql, val)
                                totalsongs = mycursor.fetchall()
                                cnx.close()

                                totalsongs = totalsongs[0][0] + 1
                                cnx = cnxpool.get_connection()
                                mycursor = cnx.cursor()
                                sql = "UPDATE qp_sessionusers SET totalsongs = %s WHERE whichsession = %s AND userid = %s"
                                val = (totalsongs, sessionidfromapi, guestidfromapi)
                                mycursor.execute(sql, val)
                                cnx.commit()
                                cnx.close()

                                return jsonify({'response': "Link added to the queue"}) 
                            else:
                                # If yes then return "Video is longer than the max video lenght preference"
                                return jsonify({'response': "Video is longer than the max video lenght preference!"})
                        else:
                            # If yes then return "Song is already in the queue but not played yet"
                            return jsonify({'response': "Song is already in the queue but not played yet!"})
                    else:
                        # If yes then return "Song already played in the last " + str(timebetweensamemusic/60/60) + " hours"
                        return jsonify({'response': "Song already played in the last " + str(round(timebetweensamemusic[0][0]/60/60)) + " hours!"})
                else:
                    # If no then return "Song already played more than " + str(samemusicmaxtimes) + " times"
                    return jsonify({'response': "Song already played already " + str(samemusicmaxtimes[0][0]) + " times!"})

    # Provide skips count
    # Check if the session exists
    cnx = cnxpool.get_connection()
    mycursor = cnx.cursor()
    sql = "SELECT id FROM qp_sessions WHERE id = %s"
    val = (sessionid,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    cnx.close()

    if len(myresult) == 0:
        # If no then return "Session does not exist"
        return jsonify({'response': "Session does not exist!"})
    else:
        # If yes then check if the user is in the session
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT id FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
        val = (sessionid, guestid)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        if len(myresult) == 0:
            # If no then return "User is not in the session"
            return jsonify({'response': "User is not in the session!"})
        else:
            # If yes then return the skips count
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT skips FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
            val = (sessionid, guestid)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            return jsonify({'response': myresult[0][0]})

# Control session api skip part
@app.route('/managesessionapiskip/<sessionid>/<guestid>', methods=['POST'])
def managesessionapiskip(sessionid, guestid):
    if request.method == 'POST':
        # Check if the session exists
        cnx = cnxpool.get_connection()
        mycursor = cnx.cursor()
        sql = "SELECT * FROM qp_sessions WHERE sessionid = %s"
        val = (sessionid,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        cnx.close()

        if len(myresult) == 0:
            # If no then return "Session does not exist"
            return jsonify({'response': "Session does not exist!"})
        else:
            # If yes then check if the user is in the session
            cnx = cnxpool.get_connection()
            mycursor = cnx.cursor()
            sql = "SELECT userid FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
            val = (sessionid, guestid)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            cnx.close()

            if len(myresult) == 0:
                # If no then return "User is not in the session"
                return jsonify({'response': "User is not in the session!"})
            else:
                # If yes then check if the user has skips left
                cnx = cnxpool.get_connection()
                mycursor = cnx.cursor()
                sql = "SELECT skipsleft FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
                val = (sessionid, guestid)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                cnx.close()

                if myresult[0][0] > 0:
                    # If yes then skip song
                    cnx = cnxpool.get_connection()
                    mycursor = cnx.cursor()
                    sql = "UPDATE qp_sessions SET skipcurrent = 1 WHERE sessionid = %s"
                    val = (sessionid,)
                    mycursor.execute(sql, val)
                    cnx.commit()
                    cnx.close()

                    # Remove 1 skip from the user
                    cnx = cnxpool.get_connection()
                    mycursor = cnx.cursor()
                    sql = "UPDATE qp_sessionusers SET skipsleft = skipsleft - 1 WHERE whichsession = %s AND userid = %s"
                    val = (sessionid, guestid)
                    mycursor.execute(sql, val)
                    cnx.commit()
                    cnx.close()

                    return jsonify({'skipsleft': myresult[0][0] - 1})
                else:
                    # If no then return "No skips left"
                    return jsonify({'response': "No skips left!"})

if __name__ == '__main__':
    context = ('./ssl/localhost.crt', './ssl/localhost.key')
    app.run(host=hostIp, port=hostPort, debug=False)
    print("\n")