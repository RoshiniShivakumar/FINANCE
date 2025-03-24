const API_URL = "http://127.0.0.1:5000/transactions";

function addTransaction() {
    const userId = document.getElementById("user_id").value;
    const type = document.getElementById("type").value;
    const amount = document.getElementById("amount").value;

    if (!userId || !type || !amount) {
        alert("Please fill all fields.");
        return;
    }

    const transactionData = {
        user_id: parseInt(userId),
        type: type.toLowerCase(),
        amount: parseFloat(amount)
    };

    fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transactionData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        getTransactions();
    })
    .catch(error => console.error("Error:", error));
}

function getTransactions() {
    fetch(API_URL)
    .then(response => response.json())
    .then(data => {
        const list = document.getElementById("transactions-list");
        list.innerHTML = "";
        data.forEach(t => {
            const item = document.createElement("li");
            item.textContent = `User ${t.user_id} - ${t.type} - $${t.amount} - ${t.timestamp}`;
            list.appendChild(item);
        });
    })
    .catch(error => console.error("Error:", error));
}

window.onload = getTransactions;
