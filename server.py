import socket
import json
import threading

# ----- Data Stores -----
users = []
games = []
rentals = []

# ----- Helper Functions -----
def handle_request(data):
    """Processes client JSON commands."""
    try:
        request = json.loads(data)
        action = request.get("action")

        if action == "add_user":
            name = request.get("name")
            if not name:
                return {"status": "error", "message": "Missing user name."}
            user_id = len(users) + 1
            users.append({"user_id": user_id, "name": name})
            return {"status": "success", "message": f"User '{name}' added.", "user_id": user_id}

        elif action == "add_game":
            title = request.get("title")
            if not title:
                return {"status": "error", "message": "Missing game title."}
            game_id = len(games) + 1
            games.append({"game_id": game_id, "title": title, "available": True})
            return {"status": "success", "message": f"Game '{title}' added.", "game_id": game_id}

        elif action == "create_rental":
            user_id = request.get("user_id")
            game_id = request.get("game_id")

            # Validate
            user = next((u for u in users if u["user_id"] == user_id), None)
            game = next((g for g in games if g["game_id"] == game_id), None)

            if not user:
                return {"status": "error", "message": "User not found."}
            if not game:
                return {"status": "error", "message": "Game not found."}
            if not game["available"]:
                return {"status": "error", "message": "Game already rented."}

            rental_id = len(rentals) + 1
            rentals.append({
                "rental_id": rental_id,
                "user_id": user_id,
                "game_id": game_id,
                "returned": False
            })
            game["available"] = False
            return {"status": "success", "message": f"Rental created for user {user_id} and game {game_id}."}

        elif action == "return_rental":
            rental_id = request.get("rental_id")
            rental = next((r for r in rentals if r["rental_id"] == rental_id), None)

            if not rental:
                return {"status": "error", "message": "Rental not found."}
            if rental["returned"]:
                return {"status": "error", "message": "Rental already returned."}

            rental["returned"] = True
            # Mark the game available again
            for g in games:
                if g["game_id"] == rental["game_id"]:
                    g["available"] = True
                    break

            return {"status": "success", "message": f"Rental {rental_id} returned successfully."}

        elif action == "list_dashboard":
            return {
                "status": "success",
                "users": users,
                "games": games,
                "rentals": rentals
            }

        else:
            return {"status": "error", "message": "Unknown action."}

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ----- Client Handler -----
def client_thread(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            response = handle_request(data.decode())
            conn.sendall(json.dumps(response).encode())
    print(f"Connection closed: {addr}")


# ----- Main Server Loop -----
def start_server(host="127.0.0.1", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=client_thread, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()




