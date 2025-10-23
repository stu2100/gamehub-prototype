from flask import Flask, render_template_string, request, redirect
import socket
import json

HOST = "127.0.0.1"
PORT = 5000

app = Flask(__name__)

USERNAME = ""
PASSWORD = ""

# --- Communication helper ---
def send_request(data):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    # Authenticate first
    auth_request = {"type": "auth", "username": USERNAME, "password": PASSWORD}
    client.send(json.dumps(auth_request).encode())
    auth_response = json.loads(client.recv(1024).decode())
    if auth_response.get("status") != "ok":
        client.close()
        raise Exception("Authentication failed: " + auth_response.get("message", ""))
    # Send actual request
    client.send(json.dumps(data).encode())
    response = json.loads(client.recv(8192).decode())
    client.close()
    return response

# --- Dashboard data ---
def get_dashboard_data():
    try:
        response = send_request({"action": "list_dashboard"})
        return response
    except Exception as e:
        return {"users": [], "games": [], "rentals": [], "error": str(e)}

# --- HTML Template ---
TEMPLATE = """
<!doctype html>
<title>GameHub Web Client</title>
<h1>GameHub Web Client</h1>

<h2>Create Rental</h2>
<form method="post" action="/create_rental">
  User: 
  <select name="user_id">
    {% for u in users %}
      <option value="{{ u.user_id }}">{{ u.name }} (ID: {{ u.user_id }})</option>
    {% endfor %}
  </select>
  Game: 
  <select name="game_id">
    {% for g in games %}
      <option value="{{ g.game_id }}">{{ g.title }} (ID: {{ g.game_id }})</option>
    {% endfor %}
  </select>
  <input type="submit" value="Create Rental">
</form>

<h2>Return Rental</h2>
<form method="post" action="/return_rental">
  Rental: 
  <select name="rental_id">
    {% for r in rentals %}
      <option value="{{ r.rental_id }}">Rental {{ r.rental_id }}: User {{ r.user_id }} - Game {{ r.game_id }}</option>
    {% endfor %}
  </select>
  <input type="submit" value="Return Rental">
</form>

<h2>Dashboard</h2>

<h3>Users</h3>
<ul>
{% for u in users %}
  <li>ID: {{ u.user_id }}, Name: {{ u.name }}, Email: {{ u.email }}</li>
{% endfor %}
</ul>

<h3>Games</h3>
<ul>
{% for g in games %}
  <li>ID: {{ g.game_id }}, Title: {{ g.title }}, Stock: {{ g.stock }}, Available: {{ g.available }}</li>
{% endfor %}
</ul>

<h3>Rentals</h3>
<ul>
{% for r in rentals %}
  <li>Rental ID: {{ r.rental_id }}, User ID: {{ r.user_id }}, Game ID: {{ r.game_id }}, Returned: {{ r.returned }}, Late Fee: ${{ r.late_fee }}, Due: {{ r.due_date }}</li>
{% endfor %}
</ul>

{% if error %}
<p style="color:red">Error: {{ error }}</p>
{% endif %}
"""

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    data = get_dashboard_data()
    return render_template_string(TEMPLATE, users=data.get("users", []),
                                  games=data.get("games", []),
                                  rentals=data.get("rentals", []),
                                  error=data.get("error", None))

@app.route("/create_rental", methods=["POST"])
def create_rental():
    try:
        user_id = int(request.form["user_id"])
        game_id = int(request.form["game_id"])
        send_request({"action": "create_rental", "user_id": user_id, "game_id": game_id})
    except Exception as e:
        print("Error creating rental:", e)
    return redirect("/")

@app.route("/return_rental", methods=["POST"])
def return_rental():
    try:
        rental_id = int(request.form["rental_id"])
        send_request({"action": "return_rental", "rental_id": rental_id})
    except Exception as e:
        print("Error returning rental:", e)
    return redirect("/")

if __name__ == "__main__":
    # Ask for login once at start
    USERNAME = input("Enter server username: ")
    PASSWORD = input("Enter server password: ")
    app.run(host="0.0.0.0", port=8080)
