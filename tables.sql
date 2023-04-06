CREATE TABLE qp_sessions (sessionid VARCHAR(255), sessioncode VARCHAR(255), skipsperuser int(20), timebetweensamemusic int(20), samemusicmaxtimes int(20), creationdate DATETIME);
CREATE TABLE qp_sessionusers (whichsession VARCHAR(255), userid VARCHAR(255), username VARCHAR(255), skipsleft int(20), totalsongs int(20));
CREATE TABLE qp_sessionmusics (whichsession VARCHAR(255), sentbywhoid VARCHAR(255), url VARCHAR(5000), videoname VARCHAR(255), videolenght int(20), thumbnailurl VARCHAR(5000));