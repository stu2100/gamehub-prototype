import socket
import json
import datetime

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# --- Helper to send request to server ---
def send_request(request_dict):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(json.dumps(request_dict).encode())
            data = s.recv(8192)
            if not data:
                print("No response from server")
                return None
            return json.loads(data.decode())
    except Exception as e:
        print("Error:", e)
        return None

# --- Dashboard display ---
def show_dashboard():
    response = send_request({"action": "list_dashboard"})
    if not response:
        return

    print("\n=== USERS ===")
    for u in response.get("users", []):
        print(f"ID: {u.get('user_id', 'N/A')}, Name: {u.get('name', 'N/A')}")

    print("\n=== GAMES ===")
    for g in response.get("games", []):
        game_id = g.get("game_id", "N/A")
        title = g.get("title", "N/A")
        stock = g.get("stock", "N/A")
        available = g.get("available", "N/A")
        print(f"ID: {game_id}, Title: {title}, Stock: {stock}, Available: {available}")

    print("\n=== RENTALS ===")
    for r in response.get("rentals", []):
        rental_id = r.get("rental_id", "N/A")
        user_id = r.get("user_id", "N/A")
        game_id = r.get("game_id", "N/A")
        returned = r.get("returned", "N/A")
        late_fee = r.get("late_fee", "N/A")
        due_date = r.get("due_date", "N/A")
        print(f"Rental ID: {rental_id}, User ID: {user_id}, Game ID: {game_id}, Returned: {returned}, Late Fee: ${late_fee}, Due: {due_date}")

# --- Menu actions ---
def add_user():
    name = input("Enter user name: ")
    response = send_request({"action": "add_user", "name": name})
    if response:
        print(response.get("message", "User added"))

def add_game():
    title = input("Enter game title: ")
    try:
        stock = int(input("Enter stock quantity: "))
    except ValueError:
        print("Stock must be a number")
        return
    response = send_request({"action": "add_game", "title": title, "stock": stock})
    if response:
        print(response.get("message", "Game added"))

def create_rental():
    try:
        user_id = int(input("Enter user ID: "))
        game_id = int(input("Enter game ID: "))
    except ValueError:
        print("IDs must be numbers")
        return
    response = send_request({"action": "create_rental", "user_id": user_id, "game_id": game_id})
    if response:
        print(response.get("message", "Rental created"))

def return_rental():
    try:
        rental_id = int(input("Enter rental ID to return: "))
    except ValueError:
        print("Rental ID must be a number")
        return
    response = send_request({"action": "return_rental", "rental_id": rental_id})
    if response:
        print(response.get("message", "Rental returned"))

# --- Main menu ---
def main():
    while True:
        print("\n--- GameHub Menu ---")
        print("1. Add user")
        print("2. Add game")
        print("3. Create rental")
        print("4. Return rental")
        print("5. Show dashboard")
        print("6. Exit")

        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_user()
        elif choice == "2":
            add_game()
        elif choice == "3":
            create_rental()
        elif choice == "4":
            return_rental()
        elif choice == "5":
            show_dashboard()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again")

if __name__ == "__main__":
    main()
