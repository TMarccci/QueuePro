from flask import Flask, session, redirect, request, url_for, render_template, Response, jsonify, send_file, send_from_directory
import mysql.connector, uuid, time, segno, datetime
from pytube import YouTube 

hostIp = 'localhost'
hostPort = 5000
app = Flask(__name__)

host = 'vpn.tmarccci.hu'
user = 'pythonuser'
password = 'nn253g8v@'
database = 'queuepro'

mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
)

mycursor = mydb.cursor()

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

        sql = "INSERT INTO qp_sessions (sessionid, sessioncode, skipsperuser, timebetweensamemusic, samemusicmaxtimes, 	maxvideolenght, creationdate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (sessionid, sessioncode, skipsperuser, timebetweensamemusic, samemusicmaxtimes, maxvideolenght, creationdate)
        mycursor.execute(sql, val)

        mydb.commit()

        # Generate QR code for session
        generate_qr_code(sessionid)

        # Return room's session id to make it reachable: data.roomid in javascript
        return jsonify({'roomid': sessionid})

@app.route('/hostsession/<sessionid>')
def hostsessionid(sessionid):
    return render_template('hostsession.html', sessionid=sessionid, title="QueuePro - Host Session")

# Generate QR code for session
def generate_qr_code(sessionid):
    link = f'http://{hostIp}:{hostPort}/joinsession/{sessionid}'

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
        # Later, we will get the queue from the database
        # Prepare the data
        data = {
            'queue': [
                {
                    'name': 'Lady Gaga - Bad Romance (Gaga Live Sydney Monster Hall)',
                    'sentby': 'TMarccci',
                    'placeinqueue': '1',
                    'thumbnailurl': 'https://img.youtube.com/vi/OXm6_v0rMCY/mqdefault.jpg',
                    'videolenght': '5:00',
                },
                {
                    'name': 'Michael Jackson - Billie Jean (Official Video)',
                    'artist': 'TMarccci',
                    'album': '2',
                    'duration': '3:00',
                    'votes': '3:00',
                },
            ]
        }

        while True:
            # Start a timer on an other thread continue process after 5 seconds
            # This is to simulate the time it takes to get the queue from the database
            # This is not needed in the final product


            yield f"data: {data} \n\n"
    return Response(get_data(), mimetype='text/event-stream')

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

        sql = "SELECT sessionid FROM qp_sessions WHERE sessioncode = %s"
        val = (joincode,)
        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

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
            sql = "SELECT username FROM qp_sessionusers WHERE whichsession = %s AND username = %s"
            val = (sessionidfromapi, guestname)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()

            if len(myresult) != 0:
                return jsonify({'response': "Name already taken"})
            else:
                # Table cols: whichsession	userid	username	skipsleft	totalsongs
                sql = "INSERT INTO qp_sessionusers (whichsession, userid, username, skipsleft, totalsongs) VALUES (%s, %s, %s, %s, %s)"
                val = (sessionidfromapi, guestid, guestname, skipsleft, totalsongs)
                mycursor.execute(sql, val)
                mydb.commit()
                return jsonify({'response': guestid})

# Control session page, the user can control the session here
@app.route('/managesession/<sessionid>/<guestid>')
def managesessionid(sessionid, guestid):
    # Get the users remaining skips
    sql = "SELECT skipsleft FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
    val = (sessionid, guestid)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    mydb.commit()

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
        # 	id     whichsession    sentbywhoid url placeinqueue    isplayed    ifplayedwhen(datetime)    videoname   videolenght     thumbnailurl
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
        sql = "SELECT timebetweensamemusic FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        timebetweensamemusic = mycursor.fetchall()
        mydb.commit()

        # Get max times a song can be played
        sql = "SELECT samemusicmaxtimes FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        samemusicmaxtimes = mycursor.fetchall()
        mydb.commit()

        # Get max video lenght preference
        sql = "SELECT maxvideolenght FROM qp_sessions WHERE sessionid = %s"
        val = (sessionidfromapi,)
        mycursor.execute(sql, val)
        maxvideolenght = mycursor.fetchall()
        mydb.commit()

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
        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s"
        val = (sessionidfromapi, link)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        mydb.commit()

        if len(myresult) == 0:
            # If no then check if the video is longer than the max video lenght preference
            if videolenght <= maxvideolenght[0][0]:
                # If no then add it to the queue
                # Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
                sql = "SELECT placeinqueue FROM qp_sessionmusics WHERE whichsession = %s ORDER BY id DESC"
                val = (sessionidfromapi,)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                mydb.commit()

                if len(myresult) == 0:
                    placeinqueue = 1
                else:
                    placeinqueue = myresult[0][0] + 1

                # Add to the queue
                sql = "INSERT INTO qp_sessionmusics (whichsession, sentbywhoid, url, placeinqueue, isplayed, ifplayedwhen, videoname, videolenght, thumbnailurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (sessionidfromapi, guestidfromapi, link, placeinqueue, 0, 0, videoname, videolenght, thumbnailurl)
                mycursor.execute(sql, val)
                mydb.commit()

                # Add total songs +1 to the users stat
                # qp_sessionusers -> the sessions current users totalsongs
                sql = "SELECT totalsongs FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
                val = (sessionidfromapi, guestidfromapi)
                mycursor.execute(sql, val)
                totalsongs = mycursor.fetchall()
                mydb.commit()

                totalsongs = totalsongs[0][0] + 1
                sql = "UPDATE qp_sessionusers SET totalsongs = %s WHERE whichsession = %s AND userid = %s"
                val = (totalsongs, sessionidfromapi, guestidfromapi)
                mycursor.execute(sql, val)
                mydb.commit()

                return jsonify({'response': "Link added to the queue"}) 
            else:
                # If yes then return "Video is longer than the max video lenght preference"
                return jsonify({'response': "Video is longer than the max video lenght preference!"})
        else:
            # If yes then check if it is on the queue and not played
            sql = "SELECT isplayed FROM qp_sessionmusics WHERE whichsession = %s AND url = %s"
            val = (sessionidfromapi, link)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            mydb.commit()

            if myresult[0][0] == 0:
                # If no then return "Song is already in the queue but not played yet"
                return jsonify({'response': "Song is already in the queue but not played yet!"})
            else:
                # If yes then check if it is playeable again (samemusicmaxtimes)
                sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 0"
                val = (sessionidfromapi, link)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                mydb.commit()

                if len(myresult) < samemusicmaxtimes[0][0]-1:
                    # If yes then check if it is played in the last x time (timebetweensamemusic)
                    sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 1 AND ifplayedwhen > %s"
                    val = (sessionidfromapi, link, datetime.datetime.now() - datetime.timedelta(seconds=timebetweensamemusic[0][0]))
                    mycursor.execute(sql, val)
                    myresult = mycursor.fetchall()
                    mydb.commit()

                    if len(myresult) == 0:
                        # If no then check it that is it in the queue already waiting to be played
                        sql = "SELECT id FROM qp_sessionmusics WHERE whichsession = %s AND url = %s AND isplayed = 0"
                        val = (sessionidfromapi, link)
                        mycursor.execute(sql, val)
                        myresult = mycursor.fetchall()
                        mydb.commit()

                        if len(myresult) == 0:
                            # If no then check if the video is longer than the max video lenght preference
                            if videolenght <= maxvideolenght[0][0]:
                                # If no then add it to the queue
                                # Add it to the queue the way get the last place in the queue and add 1. If there is no queue then add 1
                                sql = "SELECT placeinqueue FROM qp_sessionmusics WHERE whichsession = %s ORDER BY id DESC"
                                val = (sessionidfromapi,)
                                mycursor.execute(sql, val)
                                myresult = mycursor.fetchall()
                                mydb.commit()

                                if len(myresult) == 0:
                                    placeinqueue = 1
                                else:
                                    placeinqueue = myresult[0][0] + 1

                                # Add to the queue
                                sql = "INSERT INTO qp_sessionmusics (whichsession, sentbywhoid, url, placeinqueue, isplayed, ifplayedwhen, videoname, videolenght, thumbnailurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                val = (sessionidfromapi, guestidfromapi, link, placeinqueue, 0, 0, videoname, videolenght, thumbnailurl)
                                mycursor.execute(sql, val)
                                mydb.commit()

                                # Add total songs +1 to the users stat
                                # qp_sessionusers -> the sessions current users totalsongs
                                sql = "SELECT totalsongs FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
                                val = (sessionidfromapi, guestidfromapi)
                                mycursor.execute(sql, val)
                                totalsongs = mycursor.fetchall()
                                mydb.commit()

                                totalsongs = totalsongs[0][0] + 1
                                sql = "UPDATE qp_sessionusers SET totalsongs = %s WHERE whichsession = %s AND userid = %s"
                                val = (totalsongs, sessionidfromapi, guestidfromapi)
                                mycursor.execute(sql, val)
                                mydb.commit()

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
    sql = "SELECT id FROM qp_sessions WHERE id = %s"
    val = (sessionid,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    mydb.commit()

    if len(myresult) == 0:
        # If no then return "Session does not exist"
        return jsonify({'response': "Session does not exist!"})
    else:
        # If yes then check if the user is in the session
        sql = "SELECT id FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
        val = (sessionid, guestid)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        mydb.commit()

        if len(myresult) == 0:
            # If no then return "User is not in the session"
            return jsonify({'response': "User is not in the session!"})
        else:
            # If yes then return the skips count
            sql = "SELECT skips FROM qp_sessionusers WHERE whichsession = %s AND userid = %s"
            val = (sessionid, guestid)
            mycursor.execute(sql, val)
            myresult = mycursor.fetchall()
            mydb.commit()

            return jsonify({'response': myresult[0][0]})

if __name__ == '__main__':
    context = ('./ssl/localhost.crt', './ssl/localhost.key')
    app.run(host=hostIp, port=hostPort, debug=False, ssl_context=context)
    print("\n")