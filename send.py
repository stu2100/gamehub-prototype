import socket
import json
import re

HOST = "127.0.0.1"
PORT = 5000

def send_request(client, request):
    client.send(json.dumps(request).encode())
    response = json.loads(client.recv(8192).decode())
    return response

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def add_user(client):
    name = input("Enter user name: ")
    while True:
        email = input("Enter email: ")
        if not is_valid_email(email):
            print("Invalid email format. Try again.")
        else:
            break
    while True:
        password = input("Enter password: ")
        pattern_pw = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern_pw, password):
            print("Password must be at least 8 characters, include upper/lowercase, number, and special char")
        else:
            break
    request = {"action": "add_user", "name": name, "email": email, "password": password}
    response = send_request(client, request)
    print(response.get("message", response))

def add_game(client):
    title = input("Enter game title: ")
    while True:
        try:
            stock = int(input("Enter stock quantity: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    request = {"action": "add_game", "title": title, "stock": stock}
    response = send_request(client, request)
    print(response.get("message", response))

def create_rental(client):
    try:
        user_id = int(input("Enter user ID: "))
        game_id = int(input("Enter game ID: "))
    except ValueError:
        print("Invalid input. IDs must be numbers.")
        return
    request = {"action": "create_rental", "user_id": user_id, "game_id": game_id}
    response = send_request(client, request)
    print(response.get("message", response))

def return_rental(client):
    try:
        rental_id = int(input("Enter rental ID: "))
    except ValueError:
        print("Invalid input. Rental ID must be a number.")
        return
    request = {"action": "return_rental", "rental_id": rental_id}
    response = send_request(client, request)
    print(response.get("message", response))

def show_dashboard(client):
    request = {"action": "list_dashboard"}
    response = send_request(client, request)

    print("\n=== USERS ===")
    for u in response.get("users", []):
        print(f"ID: {u.get('user_id')}, Name: {u.get('name')}, Email: {u.get('email')}")

    print("\n=== GAMES ===")
    for g in response.get("games", []):
        stock = g.get("stock", "N/A")
        available = g.get("available", "N/A")
        print(f"ID: {g.get('game_id')}, Title: {g.get('title')}, Stock: {stock}, Available: {available}")

    print("\n=== RENTALS ===")
    for r in response.get("rentals", []):
        returned = r.get("returned", "N/A")
        late_fee = r.get("late_fee", "N/A")
        due_date = r.get("due_date", "N/A")
        print(f"Rental ID: {r.get('rental_id')}, User ID: {r.get('user_id')}, Game ID: {r.get('game_id')}, Returned: {returned}, Late Fee: ${late_fee}, Due: {due_date}")
    print("")

def authenticate(client):
    print("Please log in to GameHub server:")
    username = input("Username: ")
    password = input("Password: ")
    auth_request = {"type": "auth", "username": username, "password": password}
    client.send(json.dumps(auth_request).encode())
    auth_response = json.loads(client.recv(1024).decode())
    if auth_response.get("status") != "ok":
        print("Authentication failed:", auth_response.get("message"))
        return False
    print(auth_response.get("message"))
    return True

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    if not authenticate(client):
        client.close()
        return

    while True:
        print("\n--- GameHub Menu ---")
        print("1. Add user")
        print("2. Add game")
        print("3. Create rental")
        print("4. Return rental")
        print("5. Show dashboard")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            add_user(client)
        elif choice == "2":
            add_game(client)
        elif choice == "3":
            create_rental(client)
        elif choice == "4":
            return_rental(client)
        elif choice == "5":
            show_dashboard(client)
        elif choice == "6":
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Try again.")

    client.close()

if __name__ == "__main__":
    main()
