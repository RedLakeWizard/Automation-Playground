from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "place-holder"  

USERS = {
    "test_user": "secret123",
    "admin": "adminpass"
}

@app.route("/")
def index_redirects_to_login():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    # to dashboard if already logged in
    if "username" in session and request.method == "GET":
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in USERS and USERS[username] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
