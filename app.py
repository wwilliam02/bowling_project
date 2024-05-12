from test import query_db, init_db
from flask import Flask, send_from_directory, render_template, request, session


app = Flask(__name__, template_folder= "template")
init_db(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # secret key



@app.route("/",methods=["GET"])
def start_page():
    return send_from_directory("static","index.html")





@app.route("/login", methods=["POST"])
def login():
      

    email = request.form["email"]
    passWord = request.form["password"]
    print("email: ", email)
    print("password: ", passWord)
    player = query_db("SELECT * from players WHERE email = ? and password = ?", [email, passWord], one=True)
    if player == None:
        print("invalid")
        error_message = "Invalid email or password. Please try again."
        return render_template("login.html", error_message = error_message)
    else:
        session["player_id"] = player["PlayerID"]
        session["Fname"] = player["Fname"]
        print("player: ", player["Fname"])
        return render_template("logged_in.html", player=player["Fname"])


@app.route('/users', methods=["GET"])
def get_users():
    return render_template('users.html', players=query_db('SELECT * FROM Players'))



@app.route('/logout', methods=["POST"])
def logout():

    session.clear()
    return send_from_directory("static", "index.html")

@app.route('/book_game', methods=["GET"])
def get_book_game():
    lanes = query_db("SELECT * FROM bowlingLanes")
    return render_template("book_game.html", lanes=lanes )


@app.route('/bookings', methods=["GET"])
def get_bookings():
    return render_template("bookings.html", bookings=query_db('SELECT * FROM Bookings'))

@app.route("/logged_in")
def show_logged_in():
    return render_template("logged_in.html", player=session["Fname"])

@app.route('/book_game', methods=["POST"])
def book_game():

    
    player_id = session["player_id"]
    date = request.form["date"]
    lane_id = request.form["lane_id"]
    start_time = request.form["start_time"]
    print("lane ID: " + lane_id)


    booking = query_db("SELECT * from Bookings WHERE date = ? and laneID = ? and startTime = ?", [date, lane_id, start_time], one=True)

    if booking == None:
        #free lane
        query_db("INSERT INTO bookings (startTime, endTime, laneID, playerID, date) VALUES(?, strftime('%H:%M',?, '+1 hour'), ?, ?, ?) ", [start_time, start_time, lane_id, player_id, date], commit=True)
        
    
        return render_template("book_game.html", booked=False, date=date, lane_id=lane_id, start_time=start_time)
    else:
        #already booked 
        return render_template("book_game.html", booked=True)




@app.route("/booked_games")
def show_booked_games():
    player_ID = session["player_id"]
    return render_template("bookings.html", bookings=query_db('SELECT * FROM Bookings INNER JOIN BowlingLanes ON Bookings.LaneID = BowlingLanes.laneID  WHERE playerID = ?', [player_ID]))


@app.route("/previous_games", methods=["GET"])
def show_previous_games():
    player_ID = session["player_id"]
    # query_db("INSERT INTO previousGames(date, score, playerID) VALUES ('2020-01-11', 360, ?) ", [player_ID], commit=True)
    
    return render_template("previous_games.html", previousGames=query_db('SELECT * FROM previousGames WHERE playerID = ?', [player_ID]), 
                           numOfGames=query_db('SELECT COUNT(?) AS numOfGames FROM previousGames WHERE playerID = ? GROUP BY playerID ',[player_ID, player_ID]))
    


@app.route("/<path:filename>", methods=["GET"])
def redirect_html(filename):
    print("FileName: ", filename)
    if filename == "":
        return send_from_directory("static", "index.html")
    return send_from_directory("static", filename + ".html")



#@app.route('/booked_games')
#def booked_games():


if __name__ == '__main__':
    app.run(debug=True, port=8080)