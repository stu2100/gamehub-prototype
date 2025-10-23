import socket
import json
from threading import Thread
from datetime import datetime, timedelta

class GameHubServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.users = {}
        self.games = {}
        self.rentals = {}
        self.next_user_id = 1
        self.next_game_id = 1
        self.next_rental_id = 1

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        try:
            data = client_socket.recv(8192)
            if not data:
                client_socket.close()
                return

            request = json.loads(data.decode())
            response = self.handle_request(request)
            client_socket.sendall(json.dumps(response).encode())
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()

    def handle_request(self, request):
        action = request.get("action")
        response = {"status": "error", "message": "Unknown action"}

        # ---- Add User ----
        if action == "add_user":
            name = request.get("name")
            if not name:
                response = {"status": "error", "message": "Name is required"}
            else:
                user_id = self.next_user_id
                self.users[user_id] = {"user_id": user_id, "name": name}
                self.next_user_id += 1
                response = {"status": "success", "message": f"User '{name}' added", "user_id": user_id}

        # ---- Add Game ----
        elif action == "add_game":
            title = request.get("title")
            stock = request.get("stock", 1)
            if not title:
                response = {"status": "error", "message": "Title is required"}
            elif not isinstance(stock, int) or stock < 0:
                response = {"status": "error", "message": "Invalid stock value"}
            else:
                game_id = self.next_game_id
                self.games[game_id] = {
                    "game_id": game_id,
                    "title": title,
                    "stock": stock,
                    "available": stock > 0
                }
                self.next_game_id += 1
                response = {"status": "success", "message": f"Game '{title}' added", "game_id": game_id}

        # ---- Create Rental ----
        elif action == "create_rental":
            user_id = request.get("user_id")
            game_id = request.get("game_id")

            if user_id not in self.users:
                response = {"status": "error", "message": f"User ID {user_id} not found"}
            elif game_id not in self.games:
                response = {"status": "error", "message": f"Game ID {game_id} not found"}
            elif self.games[game_id]["stock"] <= 0:
                response = {"status": "error", "message": f"Game ID {game_id} is out of stock"}
            else:
                rental_id = self.next_rental_id
                self.rentals[rental_id] = {
                    "rental_id": rental_id,
                    "user_id": user_id,
                    "game_id": game_id,
                    "returned": False,
                    "rental_date": datetime.now().isoformat(),
                    "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "late_fee": 0
                }
                self.games[game_id]["stock"] -= 1
                self.games[game_id]["available"] = self.games[game_id]["stock"] > 0
                self.next_rental_id += 1
                response = {"status": "success", "message": "Rental created", "rental_id": rental_id}

        # ---- Delete User ----
        elif action == "delete_user":
            user_id = request.get("user_id")
            if user_id is None:
                response = {"status": "error", "message": "user_id missing"}
            elif user_id not in self.users:
                response = {"status": "error", "message": f"User ID {user_id} not found"}
            else:
                del self.users[user_id]
                response = {"status": "success", "message": f"User ID {user_id} deleted"}

        # ---- Delete Game ----
        elif action == "delete_game":
            game_id = request.get("game_id")
            if game_id is None:
                response = {"status": "error", "message": "game_id missing"}
            elif game_id not in self.games:
                response = {"status": "error", "message": f"Game ID {game_id} not found"}
            else:
                del self.games[game_id]
                response = {"status": "success", "message": f"Game ID {game_id} deleted"}

        # ---- Update Game Stock ----
        elif action == "update_stock":
            game_id = request.get("game_id")
            new_stock = request.get("stock")
            if game_id is None:
                response = {"status": "error", "message": "game_id missing"}
            elif game_id not in self.games:
                response = {"status": "error", "message": f"Game ID {game_id} not found"}
            elif not isinstance(new_stock, int) or new_stock < 0:
                response = {"status": "error", "message": "Invalid stock value"}
            else:
                self.games[game_id]["stock"] = new_stock
                self.games[game_id]["available"] = new_stock > 0
                response = {"status": "success", "message": f"Game ID {game_id} stock updated to {new_stock}"}

        # ---- Return Rental ----
        elif action == "return_rental":
            rental_id = request.get("rental_id")
            if rental_id not in self.rentals:
                response = {"status": "error", "message": f"Rental ID {rental_id} not found"}
            elif self.rentals[rental_id]["returned"]:
                response = {"status": "error", "message": "Rental already returned"}
            else:
                rental = self.rentals[rental_id]
                rental["returned"] = True
                return_date = datetime.now()
                due_date = datetime.fromisoformat(rental["due_date"])
                days_late = (return_date - due_date).days
                late_fee = max(0, days_late * 2)  # $2 per late day
                rental["late_fee"] = late_fee

                # Increment game stock
                game_id = rental["game_id"]
                if game_id in self.games:
                    self.games[game_id]["stock"] += 1
                    self.games[game_id]["available"] = True

                response = {"status": "success", "message": f"Rental returned. Late fee: ${late_fee}"}

        # ---- Dashboard / List ----
        elif action == "list_dashboard":
            response = {
                "status": "success",
                "users": list(self.users.values()),
                "games": list(self.games.values()),
                "rentals": list(self.rentals.values())
            }

        return response

if __name__ == "__main__":
    server = GameHubServer()
    server.start()
