
const loginForm = document.getElementById("login-form");

if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
}

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const errorElement = document.getElementById("login-error");
    const loginButton = document.getElementById("login-button");

    errorElement.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }

        // Validate the authentication response.
        if (!data.access_token ||
            !["admin", "user"].includes(data.role)) {
            throw new Error("Invalid authentication response.");
        }

        // Store authentication information for this browser tab.
        sessionStorage.setItem("access_token", data.access_token);
        sessionStorage.setItem("username", data.username);
        sessionStorage.setItem("role", data.role);

        // Redirect according to the authenticated user's role.
        if (data.role === "admin") {
            window.location.href = "/admin";
        } else {
            window.location.href = "/user";
        }

    } catch (error) {
        errorElement.textContent = error.message;

    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
}
