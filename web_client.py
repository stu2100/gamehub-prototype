from flask import Flask, render_template_string, request, redirect
import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

app = Flask(__name__)

# --- Helper function to communicate with server ---
def send_request(request_dict):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(json.dumps(request_dict).encode())
            data = s.recv(8192)
            if not data:
                return {"status": "error", "message": "No response from server"}
            return json.loads(data.decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Helper to format dashboard safely ---
def get_dashboard_data():
    response = send_request({"action": "list_dashboard"})
    dashboard_lines = []
    users_list = []
    games_list = []

    if not response:
        dashboard_lines.append("Error fetching dashboard.")
        return dashboard_lines, users_list, games_list

    # Users
    users_list = response.get("users", [])
    dashboard_lines.append("=== USERS ===")
    for u in users_list:
        dashboard_lines.append(f"ID: {u.get('user_id', 'N/A')}, Name: {u.get('name', 'N/A')}")

    # Games
    games_list = response.get("games", [])
    dashboard_lines.append("\n=== GAMES ===")
    for g in games_list:
        game_id = g.get("game_id", "N/A")
        title = g.get("title", "N/A")
        stock = g.get("stock", "N/A")
        available = g.get("available", "N/A")
        dashboard_lines.append(f"ID: {game_id}, Title: {title}, Stock: {stock}, Available: {available}")

    # Rentals
    dashboard_lines.append("\n=== RENTALS ===")
    for r in response.get("rentals", []):
        rental_id = r.get("rental_id", "N/A")
        user_id = r.get("user_id", "N/A")
        game_id = r.get("game_id", "N/A")
        returned = r.get("returned", "N/A")
        late_fee = r.get("late_fee", "N/A")
        due_date = r.get("due_date", "N/A")
        dashboard_lines.append(
            f"Rental ID: {rental_id}, User ID: {user_id}, Game ID: {game_id}, "
            f"Returned: {returned}, Late Fee: ${late_fee}, Due: {due_date}"
        )

    return dashboard_lines, users_list, games_list

# --- HTML template ---
template = """
<!DOCTYPE html>
<html>
<head>
    <title>GameHub Web Client</title>
</head>
<body>
    <h1>GameHub Web Client</h1>

    <h2>Create Rental</h2>
    <form method="post" action="/create_rental">
        User:
        <select name="user_id">
            {% for user in users %}
            <option value="{{ user['user_id'] }}">{{ user['name'] }} (ID: {{ user['user_id'] }})</option>
            {% endfor %}
        </select>

        Game:
        <select name="game_id">
            {% for game in games %}
            <option value="{{ game['game_id'] }}">{{ game['title'] }} (ID: {{ game['game_id'] }})</option>
            {% endfor %}
        </select>

        <input type="submit" value="Create Rental">
    </form>

    <h2>Return Rental</h2>
    <form method="post" action="/return_rental">
        Rental ID: <input type="text" name="rental_id">
        <input type="submit" value="Return Rental">
    </form>

    <h2>Dashboard</h2>
    <form method="get" action="/">
        <input type="submit" value="Refresh Dashboard">
    </form>

    <pre>
{% for line in dashboard %}
{{ line }}
{% endfor %}
    </pre>

</body>
</html>
"""

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    dashboard_lines, users_list, games_list = get_dashboard_data()
    return render_template_string(template, dashboard=dashboard_lines, users=users_list, games=games_list)

@app.route("/create_rental", methods=["POST"])
def create_rental():
    try:
        user_id = int(request.form["user_id"])
        game_id = int(request.form["game_id"])
        send_request({"action": "create_rental", "user_id": user_id, "game_id": game_id})
    except:
        pass
    return redirect("/")

@app.route("/return_rental", methods=["POST"])
def return_rental():
    try:
        rental_id = int(request.form["rental_id"])
        send_request({"action": "return_rental", "rental_id": rental_id})
    except:
        pass
    return redirect("/")

# --- Run Flask server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
