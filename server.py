import socket
import json
import datetime
import logging
import threading
import re

# --- Logging setup ---
logging.basicConfig(filename="server_log.txt", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

# --- Server data ---
users = []
games = []
rentals = []

next_user_id = 1
next_game_id = 1
next_rental_id = 1

# --- Basic authentication for admin clients ---
VALID_USERS = {
    "admin": "password123",
    "tester": "gamehub"
}

# --- Helper functions ---
def calculate_late_fee(rental):
    if rental.get("returned") and rental.get("due_date"):
        due = datetime.datetime.strptime(rental["due_date"], "%Y-%m-%d")
        returned = datetime.datetime.strptime(rental["return_date"], "%Y-%m-%d")
        days_late = (returned - due).days
        return max(0, days_late * 2)  # $2 per day late
    return 0

def handle_client(client_socket, address):
    global next_user_id, next_game_id, next_rental_id
    try:
        # --- Authentication ---
        auth_data = client_socket.recv(1024).decode()
        auth_json = json.loads(auth_data)
        logging.info(f"Received (auth): {auth_json}")

        if auth_json.get("type") != "auth" or \
           auth_json.get("username") not in VALID_USERS or \
           auth_json.get("password") != VALID_USERS[auth_json["username"]]:
            response = {"status": "error", "message": "Authentication failed"}
            client_socket.send(json.dumps(response).encode())
            client_socket.close()
            return
        else:
            client_socket.send(json.dumps({"status": "ok", "message": "Authenticated"}).encode())

        # --- Handle requests ---
        while True:
            data = client_socket.recv(8192)
            if not data:
                break

            try:
                request = json.loads(data.decode())
                logging.info(f"Received: {request}")

                action = request.get("action")

                # --- Commands ---
                if action == "add_user":
                    name = request.get("name")
                    email = request.get("email")
                    password = request.get("password")
                    if not name or not email or not password:
                        raise KeyError("name, email, or password missing")
                    # Email validation
                    pattern_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
                    if not re.match(pattern_email, email):
                        response = {"status": "error", "message": "Invalid email format"}
                    else:
                        # Password complexity check
                        pattern_pw = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                        if not re.match(pattern_pw, password):
                            response = {"status": "error", "message": "Password must be at least 8 characters, include upper/lowercase, number, and special char"}
                        else:
                            user = {"user_id": next_user_id, "name": name, "email": email, "password": password}
                            users.append(user)
                            next_user_id += 1
                            response = {"status": "ok", "message": f"User {name} added"}

                elif action == "add_game":
                    title = request.get("title")
                    stock = request.get("stock")
                    if title is None or stock is None:
                        raise KeyError("title or stock missing")
                    game = {"game_id": next_game_id, "title": title, "stock": stock, "available": True}
                    games.append(game)
                    next_game_id += 1
                    response = {"status": "ok", "message": f"Game {title} added"}

                elif action == "create_rental":
                    user_id = request.get("user_id")
                    game_id = request.get("game_id")
                    if user_id is None or game_id is None:
                        raise KeyError("user_id or game_id missing")
                    rental = {
                        "rental_id": next_rental_id,
                        "user_id": user_id,
                        "game_id": game_id,
                        "returned": False,
                        "late_fee": 0,
                        "due_date": (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                    }
                    rentals.append(rental)
                    next_rental_id += 1
                    response = {"status": "ok", "message": f"Rental {rental['rental_id']} created"}

                elif action == "return_rental":
                    rental_id = request.get("rental_id")
                    if rental_id is None:
                        raise KeyError("rental_id missing")
                    rental = next((r for r in rentals if r["rental_id"] == rental_id), None)
                    if rental:
                        rental["returned"] = True
                        rental["return_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                        rental["late_fee"] = calculate_late_fee(rental)
                        response = {"status": "ok", "message": f"Rental {rental_id} returned"}
                    else:
                        response = {"status": "error", "message": "Rental not found"}

                elif action == "list_dashboard":
                    response = {"users": users, "games": games, "rentals": rentals}

                else:
                    response = {"status": "error", "message": "Unknown action"}

                logging.info(f"Responded: {response}")
                client_socket.send(json.dumps(response).encode())

            except KeyError as ke:
                logging.error(f"Missing key: {ke}")
                client_socket.send(json.dumps({"status": "error", "message": f"Missing key: {ke}"}).encode())
            except Exception as e:
                logging.error(f"Unhandled error: {e}")
                client_socket.send(json.dumps({"status": "error", "message": "Server error"}).encode())

    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()
        logging.info(f"Closed connection: {address}")

# --- Main server ---
def main():
    host = "0.0.0.0"
    port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"GameHub server running on {host}:{port}")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    main()
