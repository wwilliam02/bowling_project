from test import query_db, init_db
from flask import Flask, send_from_directory, render_template, request


app = Flask(__name__, template_folder= "template")
init_db(app)
@app.route("/<path:filename>", methods=["GET"])
def redirect_html(filename):
    print("FileName: ", filename)
    if filename == "":
        return send_from_directory("static", "index.html")
    return send_from_directory("static", filename + ".html")

@app.route("/Login", methods=["POST"])
def login():
    
    email = request.form["email"]
    passWord = request.form["Password"]
    print("email: ", email)
    print("password: ", passWord)
    player = query_db("SELECT * from players WHERE email = ? and password = ?", [email, passWord], one=True)
    
    print("player: ", player)
    return render_template("login.html")


@app.route('/users', methods=["GET"])
def get_users():
    return render_template('users.html', players=query_db('SELECT * FROM Players'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)

