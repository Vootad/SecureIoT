const accessToken = sessionStorage.getItem("access_token");
const userRole = sessionStorage.getItem("role");
const username = sessionStorage.getItem("username");

// Only regular users can access this dashboard.
if (!accessToken || userRole !== "user") {
    window.location.href = "/login";
}


// ------------------------------
// Authentication
// ------------------------------

function getAuthHeaders() {
    return {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json"
    };
}


function handleAuthError(status) {
    if (status === 401) {
        sessionStorage.clear();
        window.location.href = "/login";
        return true;
    }

    if (status === 403) {
        return true;
    }

    return false;
}


// ------------------------------
// Load assigned locks
// ------------------------------

async function loadLocks() {
    const tableBody = document.getElementById("locks-table-body");
    const message = document.getElementById("locks-message");

    message.textContent = "";
    tableBody.textContent = "";

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");

    loadingCell.colSpan = 4;
    loadingCell.textContent = "Loading locks...";

    loadingRow.appendChild(loadingCell);
    tableBody.appendChild(loadingRow);

    try {
        const response = await fetch("/user/locks/", {
            method: "GET",
            headers: getAuthHeaders()
        });

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load assigned locks.");
        }

        const locks = await response.json();

        tableBody.textContent = "";

        if (locks.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 4;
            cell.textContent = "You have no assigned locks.";

            row.appendChild(cell);
            tableBody.appendChild(row);
            return;
        }

        locks.forEach(lock => {
            const row = document.createElement("tr");

            // Lock identifier
            const lockCell = document.createElement("td");
            lockCell.textContent = lock.lock_id;

            // Lock status
            const statusCell = document.createElement("td");
            statusCell.textContent = lock.is_active
                ? "Active"
                : "Inactive";

            // Password input
            const passwordCell = document.createElement("td");
            const passwordInput = document.createElement("input");

            passwordInput.type = "password";
            passwordInput.placeholder = "Lock password";
            passwordInput.autocomplete = "off";
            passwordInput.className = "lock-password-input";

            passwordInput.disabled = !lock.is_active;

            passwordCell.appendChild(passwordInput);

            // Unlock button
            const actionCell = document.createElement("td");
            const unlockButton = document.createElement("button");

            unlockButton.textContent = "Unlock";
            unlockButton.className = "unlock-button";
            unlockButton.disabled = !lock.is_active;

            if (!lock.is_active) {
                passwordInput.placeholder = "Lock inactive";
            }

            unlockButton.addEventListener("click", () => {
                unlockLock(
                    lock.lock_id,
                    passwordInput,
                    unlockButton
                );
            });

            actionCell.appendChild(unlockButton);

            row.appendChild(lockCell);
            row.appendChild(statusCell);
            row.appendChild(passwordCell);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });

    } catch (error) {
        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 4;
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);
    }
}


// ------------------------------
// Unlock a lock
// ------------------------------


async function unlockLock(lockId, passwordInput, button) {
    const password = passwordInput.value;
    const message = document.getElementById("locks-message");

    if (!password) {
        message.textContent = "Please enter the lock password.";
        return;
    }

    message.textContent = "";
    button.disabled = true;
    button.textContent = "Processing...";

    try {
        const timestamp = Math.floor(Date.now() / 1000);
        const nonce = crypto.randomUUID();

        const response = await fetch("/lock/unlock", {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                lock_id: lockId,
                lock_password: password,
                timestamp: timestamp,
                nonce: nonce
            })
        });

        const data = await response.json();

        if (response.status === 401 || response.status === 403) {
            showUnlockResult(
                lockId,
                false,
                data.detail || "Unlock request failed."
            );
            return;
        }

        if (!response.ok) {
            showUnlockResult(
                lockId,
                false,
                data.detail || "Unlock request failed."
            );
            return;
        }

        showUnlockResult(
            lockId,
            true,
            data.message || "Door unlocked successfully."
        );

        passwordInput.value = "";

    } catch (error) {
        showUnlockResult(lockId, false, error.message);

    } finally {
        button.disabled = false;
        button.textContent = "Unlock";
    }
}


// ------------------------------
// Display unlock results
// ------------------------------

function showUnlockResult(lockId, success, message) {
    const resultsContainer = document.getElementById("unlock-results");

    // Remove the initial placeholder.
    if (resultsContainer.textContent === "No unlock requests yet.") {
        resultsContainer.textContent = "";
    }

    const resultItem = document.createElement("div");

    resultItem.className = success
        ? "unlock-result success"
        : "unlock-result failure";

    const title = document.createElement("strong");
    title.textContent = success
        ? `Success - ${lockId}`
        : `Failed - ${lockId}`;

    const description = document.createElement("p");
    description.textContent = message;

    const time = document.createElement("small");
    time.textContent = new Date().toLocaleString();

    resultItem.appendChild(title);
    resultItem.appendChild(description);
    resultItem.appendChild(time);

    resultsContainer.prepend(resultItem);
}


// ------------------------------
// Logout
// ------------------------------

function logout() {
    sessionStorage.clear();
    window.location.href = "/login";
}


// ------------------------------
// Event listeners
// ------------------------------

document.getElementById("refresh-locks-button")
    .addEventListener("click", loadLocks);

document.getElementById("logout-button")
    .addEventListener("click", logout);


// Load locks when the page opens.
loadLocks();