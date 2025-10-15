import socket
import json

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

# --- Main menu ---
def main():
    while True:
        print("\n--- GameHub Dashboard ---")
        print("1. Show dashboard")
        print("2. Exit")

        choice = input("Enter choice: ").strip()
        if choice == "1":
            show_dashboard()
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again")

if __name__ == "__main__":
    main()
