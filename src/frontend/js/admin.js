const API_BASE_URL = "";

const accessToken = sessionStorage.getItem("access_token");
const userRole = sessionStorage.getItem("role");

// Check whether the current browser session belongs to an admin.
if (!accessToken || userRole !== "admin") {
    window.location.href = "/login";
}

// Common headers for authenticated API requests.
function getAuthHeaders() {
    return {
        "Authorization": `Bearer ${accessToken}`,
        "Content-Type": "application/json"
    };
}

// Handle authentication and authorization errors.
function handleAuthError(status) {
    if (status === 401) {
        sessionStorage.clear();
        window.location.href = "/login";
        return true;
    }

    if (status === 403) {
        alert("You do not have permission to access this resource.");
        return true;
    }

    return false;
}


// ------------------------------
// Load and display users
// ------------------------------

async function loadUsers() {
    const tableBody = document.getElementById("users-table-body");

    tableBody.textContent = "";

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");

    loadingCell.colSpan = 6;
    loadingCell.textContent = "Loading users...";

    loadingRow.appendChild(loadingCell);
    tableBody.appendChild(loadingRow);

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/users/`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load users.");
        }

        const users = await response.json();

        tableBody.textContent = "";

        if (users.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 6;
            cell.textContent = "No users found.";

            row.appendChild(cell);
            tableBody.appendChild(row);
            return;
        }

        users.forEach(user => {
            const row = document.createElement("tr");

            const values = [
                user.id,
                user.username,
                user.role,
                user.is_active ? "Active" : "Inactive",
                user.created_at
                    ? new Date(user.created_at).toLocaleString()
                    : "-"
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            const actionCell = document.createElement("td");
            const statusButton = document.createElement("button");

            statusButton.textContent = user.is_active
                ? "Deactivate"
                : "Activate";

            statusButton.className = "secondary-button";

            // Prevent changing the admin account's status.
            if (user.role === "admin") {
                statusButton.disabled = true;
                statusButton.textContent = "Protected";
            } else {
                statusButton.addEventListener("click", () => {
                    updateUserStatus(user.id, !user.is_active);
                });
            }

            actionCell.appendChild(statusButton);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });

    } catch (error) {
        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);
    }
}


// ------------------------------
// Create a new user
// ------------------------------

async function createUser(event) {
    event.preventDefault();

    const username = document.getElementById("new-username").value.trim();
    const password = document.getElementById("new-password").value;

    const messageElement = document.getElementById("user-message");
    const button = document.getElementById("create-user-button");

    messageElement.textContent = "";
    button.disabled = true;

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/users/`,
            {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to create user.");
        }

        messageElement.textContent = "User created successfully.";

        document.getElementById("create-user-form").reset();

        await loadUsers();
        await loadPermissionOptions();

    } catch (error) {
        messageElement.textContent = error.message;

    } finally {
        button.disabled = false;
    }
}


// ------------------------------
// Activate or deactivate a user
// ------------------------------

async function updateUserStatus(userId, isActive) {
    const messageElement = document.getElementById("user-message");

    messageElement.textContent = "";

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/users/${userId}/status`,
            {
                method: "PATCH",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    is_active: isActive
                })
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to update user status.");
        }

        messageElement.textContent = "User status updated successfully.";

        await loadUsers();

    } catch (error) {
        messageElement.textContent = error.message;
    }
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

document.getElementById("create-user-form")
    .addEventListener("submit", createUser);

document.getElementById("refresh-users-button")
    .addEventListener("click", loadUsers);

document.getElementById("logout-button")
    .addEventListener("click", logout);


// Load users when the page opens.
loadUsers();

// ------------------------------
// Load and display locks
// ------------------------------

async function loadLocks() {
    const tableBody = document.getElementById("locks-table-body");

    tableBody.textContent = "";

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");

    loadingCell.colSpan = 5;
    loadingCell.textContent = "Loading locks...";

    loadingRow.appendChild(loadingCell);
    tableBody.appendChild(loadingRow);

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/locks/`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load locks.");
        }

        const locks = await response.json();

        tableBody.textContent = "";

        if (locks.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 5;
            cell.textContent = "No locks found.";

            row.appendChild(cell);
            tableBody.appendChild(row);
            return;
        }

        locks.forEach(lock => {
            const row = document.createElement("tr");

            const values = [
                lock.id,
                lock.lock_id,
                lock.is_active ? "Active" : "Inactive",
                lock.created_at
                    ? new Date(lock.created_at).toLocaleString()
                    : "-"
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            const actionCell = document.createElement("td");
            const statusButton = document.createElement("button");

            statusButton.textContent = lock.is_active
                ? "Deactivate"
                : "Activate";

            statusButton.className = "secondary-button";

            statusButton.addEventListener("click", () => {
                updateLockStatus(lock.id, !lock.is_active);
            });

            actionCell.appendChild(statusButton);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });

    } catch (error) {
        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);
    }
}


// ------------------------------
// Create a new lock
// ------------------------------

async function createLock(event) {
    event.preventDefault();

    const lockId = document.getElementById("new-lock-id").value.trim();
    const password = document.getElementById("new-lock-password").value;

    const messageElement = document.getElementById("lock-message");
    const button = document.getElementById("create-lock-button");

    messageElement.textContent = "";
    button.disabled = true;

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/locks/`,
            {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    lock_id: lockId,
                    password: password
                })
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to create lock.");
        }

        messageElement.textContent = "Lock created successfully.";

        document.getElementById("create-lock-form").reset();

        await loadLocks();

    } catch (error) {
        messageElement.textContent = error.message;

    } finally {
        button.disabled = false;
    }
}


// ------------------------------
// Activate or deactivate a lock
// ------------------------------

async function updateLockStatus(lockDbId, isActive) {
    const messageElement = document.getElementById("lock-message");

    messageElement.textContent = "";

    try {
        const response = await fetch(
            `${API_BASE_URL}/admin/locks/${lockDbId}/status`,
            {
                method: "PATCH",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    is_active: isActive
                })
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to update lock status.");
        }

        messageElement.textContent = "Lock status updated successfully.";

        await loadLocks();

    } catch (error) {
        messageElement.textContent = error.message;
    }
}


// ------------------------------
// Lock management event listeners
// ------------------------------

document.getElementById("create-lock-form")
    .addEventListener("submit", createLock);

document.getElementById("refresh-locks-button")
    .addEventListener("click", loadLocks);


// Load locks when the admin dashboard opens.
loadLocks();

// ------------------------------
// Permission Management
// ------------------------------

let availableLocks = [];

// Load users and locks for the permission form.
async function loadPermissionOptions() {
    const userSelect = document.getElementById("permission-user");
    const lockSelect = document.getElementById("permission-lock");

    try {
        const [usersResponse, locksResponse] = await Promise.all([
            fetch("/admin/users/", {
                headers: getAuthHeaders()
            }),
            fetch("/admin/locks/", {
                headers: getAuthHeaders()
            })
        ]);

        if (handleAuthError(usersResponse.status) ||
            handleAuthError(locksResponse.status)) {
            return;
        }

        if (!usersResponse.ok || !locksResponse.ok) {
            throw new Error("Failed to load users or locks.");
        }

        const users = await usersResponse.json();
        availableLocks = await locksResponse.json();

        // Only regular users should receive lock permissions.
        userSelect.textContent = "";

        const regularUsers = users.filter(
            user => user.role === "user"
        );

        if (regularUsers.length === 0) {
            userSelect.add(new Option("No users available", ""));
        } else {
            userSelect.add(new Option("Select a user", ""));

            regularUsers.forEach(user => {
                userSelect.add(
                    new Option(
                        `${user.username} (ID: ${user.id})`,
                        user.id
                    )
                );
            });
        }

        // Include inactive locks so existing permissions can be managed.
        lockSelect.textContent = "";
        lockSelect.add(new Option("Select a lock", ""));

        availableLocks.forEach(lock => {
            const status = lock.is_active ? "Active" : "Inactive";

            lockSelect.add(
                new Option(
                    `${lock.lock_id} - ${status}`,
                    lock.id
                )
            );
        });

        // Load permissions for the selected user, if any.
        if (userSelect.value) {
            await loadPermissions();
        } else {
            showEmptyPermissions();
        }

    } catch (error) {
        document.getElementById("permission-message").textContent =
            error.message;
    }
}


// Display an empty permissions table.
function showEmptyPermissions() {
    const tableBody = document.getElementById(
        "permissions-table-body"
    );

    tableBody.textContent = "";

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 3;
    cell.textContent = "Select a user to view permissions.";

    row.appendChild(cell);
    tableBody.appendChild(row);
}


// Load permissions assigned to the selected user.
async function loadPermissions() {
    const userId = document.getElementById("permission-user").value;
    const tableBody = document.getElementById(
        "permissions-table-body"
    );

    if (!userId) {
        showEmptyPermissions();
        return;
    }

    tableBody.textContent = "";

    try {
        const response = await fetch(
            `/admin/users/${userId}/locks`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load permissions.");
        }

        const permissions = await response.json();

        tableBody.textContent = "";

        if (permissions.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 3;
            cell.textContent = "This user has no lock permissions.";

            row.appendChild(cell);
            tableBody.appendChild(row);
            return;
        }

        permissions.forEach(permission => {
            const row = document.createElement("tr");

            const permissionIdCell = document.createElement("td");
            permissionIdCell.textContent = permission.id;

            const lockCell = document.createElement("td");

            const lock = availableLocks.find(
                item => item.id === permission.lock_id
            );

            lockCell.textContent = lock
                ? lock.lock_id
                : `Lock database ID: ${permission.lock_id}`;

            const actionCell = document.createElement("td");
            const revokeButton = document.createElement("button");

            revokeButton.textContent = "Revoke Access";
            revokeButton.className = "secondary-button";

            revokeButton.addEventListener("click", () => {
                revokePermission(userId, permission.lock_id);
            });

            actionCell.appendChild(revokeButton);

            row.appendChild(permissionIdCell);
            row.appendChild(lockCell);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });

    } catch (error) {
        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 3;
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);
    }
}


// Grant a lock permission to a user.
async function grantPermission(event) {
    event.preventDefault();

    const userId = document.getElementById("permission-user").value;
    const lockDbId = document.getElementById("permission-lock").value;

    const messageElement = document.getElementById("permission-message");
    const button = document.getElementById("grant-permission-button");

    messageElement.textContent = "";

    if (!userId || !lockDbId) {
        messageElement.textContent = "Select both a user and a lock.";
        return;
    }

    button.disabled = true;

    try {
        const response = await fetch(
            `/admin/users/${userId}/locks/${lockDbId}`,
            {
                method: "POST",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to grant permission."
            );
        }

        messageElement.textContent = "Permission granted successfully.";

        document.getElementById("permission-lock").value = "";

        await loadPermissions();

    } catch (error) {
        messageElement.textContent = error.message;

    } finally {
        button.disabled = false;
    }
}


// Revoke a user's permission for a specific lock.
async function revokePermission(userId, lockDbId) {
    const messageElement = document.getElementById("permission-message");

    messageElement.textContent = "";

    try {
        const response = await fetch(
            `/admin/users/${userId}/locks/${lockDbId}`,
            {
                method: "DELETE",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            let errorMessage = "Failed to revoke permission.";

            try {
                const data = await response.json();
                errorMessage = data.detail || errorMessage;
            } catch {
                // Keep the default error message.
            }

            throw new Error(errorMessage);
        }

        messageElement.textContent = "Permission revoked successfully.";

        await loadPermissions();

    } catch (error) {
        messageElement.textContent = error.message;
    }
}


// Permission management event listeners.
document.getElementById("permission-form")
    .addEventListener("submit", grantPermission);

document.getElementById("permission-user")
    .addEventListener("change", loadPermissions);

document.getElementById("refresh-permissions-button")
    .addEventListener("click", loadPermissions);


// Load permission form data when the page opens.
loadPermissionOptions();

// ------------------------------
// Audit Log Management
// ------------------------------

const AUDIT_PAGE_SIZE = 20;

let auditCurrentPage = 0;
let auditHasNextPage = false;


// Load audit logs from the backend.
async function loadAuditLogs() {
    const tableBody = document.getElementById("audit-table-body");
    const messageElement = document.getElementById("audit-message");

    const previousButton = document.getElementById(
        "previous-audit-button"
    );

    const nextButton = document.getElementById(
        "next-audit-button"
    );

    const pageInfo = document.getElementById("audit-page-info");

    messageElement.textContent = "";
    tableBody.textContent = "";

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");

    loadingCell.colSpan = 6;
    loadingCell.textContent = "Loading audit logs...";

    loadingRow.appendChild(loadingCell);
    tableBody.appendChild(loadingRow);

    try {
        const skip = auditCurrentPage * AUDIT_PAGE_SIZE;

        const response = await fetch(
            `/admin/audit-logs/?skip=${skip}&limit=${AUDIT_PAGE_SIZE}`,
            {
                method: "GET",
                headers: getAuthHeaders()
            }
        );

        if (handleAuthError(response.status)) {
            return;
        }

        if (!response.ok) {
            throw new Error("Failed to load audit logs.");
        }

        const logs = await response.json();

        tableBody.textContent = "";

        if (logs.length === 0 && auditCurrentPage > 0) {
            auditCurrentPage--;
            await loadAuditLogs();
            return;
        }

        if (logs.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 6;
            cell.textContent = "No audit logs found.";

            row.appendChild(cell);
            tableBody.appendChild(row);
        } else {
            logs.forEach(log => {
                const row = document.createElement("tr");

                const values = [
                    log.timestamp
                        ? new Date(log.timestamp).toLocaleString()
                        : "-",
                    log.username || "-",
                    log.ip_address || "-",
                    log.event_type || "-",
                    log.result || "-",
                    log.reason || "-"
                ];

                values.forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

                tableBody.appendChild(row);
            });
        }

        auditHasNextPage = logs.length === AUDIT_PAGE_SIZE;

        previousButton.disabled = auditCurrentPage === 0;
        nextButton.disabled = !auditHasNextPage;

        pageInfo.textContent = `Page ${auditCurrentPage + 1}`;

    } catch (error) {
        tableBody.textContent = "";

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent = error.message;

        row.appendChild(cell);
        tableBody.appendChild(row);

        previousButton.disabled = true;
        nextButton.disabled = true;
    }
}


// Go to the next page.
function nextAuditPage() {
    if (!auditHasNextPage) {
        return;
    }

    auditCurrentPage++;
    loadAuditLogs();
}


// Go to the previous page.
function previousAuditPage() {
    if (auditCurrentPage === 0) {
        return;
    }

    auditCurrentPage--;
    loadAuditLogs();
}


// Audit log event listeners.
document.getElementById("refresh-audit-button")
    .addEventListener("click", () => {
        auditCurrentPage = 0;
        loadAuditLogs();
    });

document.getElementById("next-audit-button")
    .addEventListener("click", nextAuditPage);

document.getElementById("previous-audit-button")
    .addEventListener("click", previousAuditPage);


// Load audit logs when the dashboard opens.
loadAuditLogs();