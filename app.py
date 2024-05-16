from test import query_db, init_db
from flask import Flask, send_from_directory, render_template, request, session


app = Flask(__name__, template_folder= "template")
init_db(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # secret key



@app.route("/",methods=["GET"])
# gets the index page
def start_page():
    return send_from_directory("static","index.html")


@app.route("/login", methods=["POST"])
#creates login functionallity
def login():
    email = request.form["email"]
    passWord = request.form["password"]

    player = query_db("SELECT * from players WHERE email = ? and password = ?", [email, passWord], one=True)
    if player == None:
        # if its the wrong email or password send back error message
        error_message = "Invalid email or password. Please try again."
        return render_template("login.html", error_message = error_message)
    else:
        # log in and render logged_in page
        session["player_id"] = player["PlayerID"]
        session["Fname"] = player["Fname"]
        return render_template("logged_in.html", player=player["Fname"])


#used for testing, show all info about all users
# @app.route('/users', methods=["GET"])
# def get_users():
#     return render_template('users.html', players=query_db('SELECT * FROM Players'))


@app.route('/register', methods=["GET"])
#shows register page
def show_register():
    return render_template('register.html')

@app.route('/register', methods=["POST"])
# register function
def register():

    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    password = request.form["password"]
    
    emailExist = query_db("SELECT * FROM players where email = ?", [email])
    # if the email exists return error message and render the template
    if emailExist:
       return render_template('register.html', error="email already used") 
    else:
        # else we created a new user and send the user back to the start page
        query_db('INSERT INTO players(fName, lName, email, password) VALUES (?,?,?,?)',[fname, lname, email, password], commit=True)
        return send_from_directory("static","index.html")


@app.route('/logout', methods=["POST"])
# logs out and shows index page
def logout():

    session.clear()
    return send_from_directory("static", "index.html")


@app.route('/bookings', methods=["GET"])
# render the bookings site
def get_bookings():
    return render_template("bookings.html", bookings=query_db('SELECT * FROM Bookings'))

@app.route("/logged_in")
#show loggend in page for the logged in user
def show_logged_in():
    return render_template("logged_in.html", player=session["Fname"], next_game=get_next_game(session["player_id"]))


@app.route('/book_game', methods=["GET"])
#show book game page
def get_book_game():
    
    if "player_id" in session:
        lanes = query_db("SELECT * FROM bowlingLanes")
        # displays the booked game directly after post
        return render_template("book_game.html", lanes=lanes, bookings=query_db("SELECT * FROM bookings INNER JOIN players ON bookings.playerID = players.playerID WHERE bookings.date > DATE('now')" ) )
    else:
        return send_from_directory("static", "index.html")

@app.route('/book_game', methods=["POST"])
#insert booking into db from booking page
def book_game():
        player_id = session["player_id"]
        date = request.form["date"]
        lane_id = request.form["lane_id"]
        start_time = request.form["start_time"]
        
        booking = query_db("SELECT * from Bookings WHERE date = ? and laneID = ? and startTime = ?", [date, lane_id, start_time], one=True)

        if booking == None:
            #free lane
            # fixa så vi får error print på hemsidan
            e = query_db("INSERT INTO bookings (startTime, endTime, laneID, playerID, date) VALUES(?, strftime('%H:%M',?, '+1 hour'), ?, ?, ?) ", [start_time, start_time, lane_id, player_id, date], commit=True)
            
            return render_template("book_game.html", booked=False, date=date, lane_id=lane_id, start_time=start_time,lanes=query_db("SELECT * FROM bowlingLanes"), error=e,
            # displays the booked game directly after post
            bookings=query_db("SELECT * FROM bookings INNER JOIN players ON bookings.playerID = players.playerID WHERE bookings.date > DATE('now')" ))
        else:
            #already booked 
            return render_template("book_game.html", booked=True,lanes=query_db("SELECT * FROM bowlingLanes"),
            # displays the booked game directly after post
            bookings=query_db("SELECT * FROM bookings INNER JOIN players ON bookings.playerID = players.playerID WHERE bookings.date > DATE('now')" ), error="Slot already booked")
    
@app.route("/booked_games", methods=["GET"])
#show bookings made for a certain player
def show_booked_games():
    player_ID = session["player_id"]
    return render_template("bookings.html", bookings=query_db('SELECT * FROM Bookings INNER JOIN BowlingLanes ON Bookings.LaneID = BowlingLanes.laneID  WHERE playerID = ?', [player_ID]))


@app.route("/remove_booking", methods=["POST"])
#delets a booking in db
def delete_booking():
    booking_id = request.form["booking_id"]
    player_ID = session["player_id"]
    # deletes bookings from your booked games with a button
    query_db("DELETE FROM bookings WHERE bookingID = ?", [booking_id], commit=True)
    return render_template("bookings.html", bookings=query_db('SELECT * FROM Bookings INNER JOIN BowlingLanes ON Bookings.LaneID = BowlingLanes.laneID  WHERE playerID = ?', [player_ID]))



@app.route("/previous_games", methods=["POST"])
# create function for previous games that lets the user insert score and date
def input_prev_game():
    player_id = session["player_id"]
    date = request.form["date"]
    score = request.form["score"]
    # inserts the given values into previous games
    query_db("INSERT INTO previousGames(date, score, playerID) VALUES (?, ?, ?) ",[date, score, player_id], commit=True)

    return render_template("previous_games.html", previousGames=query_db('SELECT * FROM previousGames INNER JOIN players ON previousGames.playerID = players.playerID WHERE previousGames.playerID = ?', [player_id]), 
    numOfGames=query_db('SELECT COUNT(?) AS numOfGames FROM previousGames WHERE playerID = ? GROUP BY playerID ',[player_id, player_id]),
    avg_score=average_score(player_id))
    


@app.route("/previous_games", methods=["GET"])
#show the previous games for a player
def show_previous_games():
    player_ID = session["player_id"]
    # query_db("INSERT INTO previousGames(date, score, playerID) VALUES ('2020-01-11', 360, ?) ", [player_ID], commit=True)
    # visar namnet på spelaren i previous games
    return render_template("previous_games.html", previousGames=query_db('SELECT * FROM previousGames INNER JOIN players ON previousGames.playerID = players.playerID WHERE previousGames.playerID = ?', [player_ID]), 
    numOfGames=query_db('SELECT COUNT(?) AS numOfGames FROM previousGames WHERE playerID = ? GROUP BY playerID ',[player_ID, player_ID]),
    avg_score=average_score(player_ID))
    

@app.route("/remove_previous_game", methods=["POST"])
# create function that lets the user delete previous games 
def remove_previous_game():
    player_ID = session["player_id"]
    game_id = request.form["gameID"]
    
    query_db("DELETE FROM previousGames WHERE gameID = ?", [game_id], commit=True)


    return render_template("previous_games.html", previousGames=query_db('SELECT * FROM previousGames INNER JOIN players ON previousGames.playerID = players.playerID WHERE previousGames.playerID = ?', [player_ID]), 
    numOfGames=query_db('SELECT COUNT(?) AS numOfGames FROM previousGames WHERE playerID = ? GROUP BY playerID ',[player_ID, player_ID]),
    avg_score=average_score(player_ID))


@app.route("/<path:filename>", methods=["GET"])
# used to redirect html
def redirect_html(filename):
    print("FileName: ", filename)
    if filename == "":
        return send_from_directory("static", "index.html")
    return send_from_directory("static", filename + ".html")



def average_score(playerID):
    # function that calculates the average score for the user
    result = query_db("SELECT ROUND(AVG(score), 1) FROM previousGames WHERE playerID = ? GROUP BY playerID", [playerID])
    if result:
        avg_score = result[0][0]
    else:
        avg_score = 0
    return avg_score


def get_next_game(playerID):
    # fetches the next game for the user and displays it on the logged_in page
    return query_db("SELECT * FROM bookings INNER JOIN bowlingLanes ON bookings.laneID = bowlingLanes.laneID WHERE playerID = ? AND date >= DATE('now') ORDER BY date, startTime LIMIT 1", [playerID])


if __name__ == '__main__':
    app.run(debug=True, port=8080)