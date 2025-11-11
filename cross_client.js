const net = require("net");
const readline = require("readline");

// Server connection details
const HOST = "127.0.0.1";
const PORT = 5000;

// --- Interactive prompt ---
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function ask(question) {
  return new Promise((resolve) => rl.question(question, resolve));
}

// --- Send request to server ---
function sendRequest(request) {
  return new Promise((resolve, reject) => {
    const client = net.createConnection(PORT, HOST, () => {
      client.write(JSON.stringify(request));
    });

    let dataBuffer = "";
    client.on("data", (data) => {
      dataBuffer += data.toString();
    });

    client.on("end", () => {
      try {
        resolve(JSON.parse(dataBuffer));
      } catch (err) {
        reject(err);
      }
    });

    client.on("error", (err) => reject(err));
  });
}

// --- Show dashboard ---
async function showDashboard() {
  try {
    const resp = await sendRequest({ action: "list_dashboard" });
    console.log("\n=== USERS ===");
    resp.users.forEach(u => console.log(`ID: ${u.user_id}, Name: ${u.name}, Email: ${u.email}`));
    console.log("\n=== GAMES ===");
    resp.games.forEach(g => console.log(`ID: ${g.game_id}, Title: ${g.title}, Stock: ${g.stock}, Available: ${g.available}`));
    console.log("\n=== RENTALS ===");
    resp.rentals.forEach(r => console.log(`Rental ID: ${r.rental_id}, User ID: ${r.user_id}, Game ID: ${r.game_id}, Returned: ${r.returned}, Late Fee: $${r.late_fee}, Due: ${r.due_date}`));
  } catch (err) {
    console.log("Error fetching dashboard:", err);
  }
}

// --- Main menu ---
async function mainMenu() {
  while (true) {
    console.log(`
--- GameHub Menu ---
1. Create rental
2. Return rental
3. Show dashboard
4. Exit
`);
    const choice = await ask("Enter choice: ");
    if (choice === "1") {
      const user_id = parseInt(await ask("Enter User ID: "));
      const game_id = parseInt(await ask("Enter Game ID: "));
      try {
        const resp = await sendRequest({ action: "create_rental", user_id, game_id });
        console.log("Create Rental Response:", resp);
      } catch (err) {
        console.log("Error:", err);
      }
    } else if (choice === "2") {
      const rental_id = parseInt(await ask("Enter Rental ID: "));
      try {
        const resp = await sendRequest({ action: "return_rental", rental_id });
        console.log("Return Rental Response:", resp);
      } catch (err) {
        console.log("Error:", err);
      }
    } else if (choice === "3") {
      await showDashboard();
    } else if (choice === "4") {
      console.log("Exiting...");
      rl.close();
      break;
    } else {
      console.log("Invalid choice.");
    }
  }
}

// --- Main ---
(async () => {
  const username = await ask("Enter server username: ");
  const password = await ask("Enter server password: ");

  try {
    const authResp = await sendRequest({ type: "auth", username, password });
    if (authResp.status !== "ok") {
      console.log("Authentication failed:", authResp.message);
      rl.close();
      return;
    }
    console.log("Authenticated successfully!");
    await mainMenu();
  } catch (err) {
    console.log("Error connecting to server:", err);
    rl.close();
  }
})();
