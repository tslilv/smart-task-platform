// Backend server URL.
// This is required because the frontend and backend now run on separate origins,
// so requests must include the full backend address.
const API_BASE = "http://127.0.0.1:5000";

let allTasks = [];
let isLoggedIn = false;

// Wrapper function around fetch that automatically adds:
// 1. The full backend URL.
// 2. credentials: "include" to send and receive session cookies
//    when communicating between different origins.
//    Without this, the user session would be lost between requests.
async function apiFetch(path, options = {}) {
    return fetch(`${API_BASE}${path}`, {
        ...options,
        credentials: "include",
    });
}

async function signup() {
    const response = await apiFetch("/signup", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        })
    });

    const data = await response.json();
    alert(data.message);

    if (data.success) {
        setLoggedIn(true);
        loadTasks();
        loadAnalytics();
    }
}

async function login() {
    const response = await apiFetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: document.getElementById("login_email").value,
            password: document.getElementById("login_password").value
        })
    });

    const data = await response.json();
    alert(data.message);

    if (data.success) {
        setLoggedIn(true);
        loadTasks();
        loadAnalytics();
    }
}

function setLoggedIn(value) {
    isLoggedIn = value;
    document.getElementById("currentUser").innerText = value ? "Yes" : "No";
}
async function checkSession() {
    const response = await apiFetch("/session");
    const data = await response.json();

    setLoggedIn(data.logged_in);

    if (data.logged_in) {
        loadTasks();
    }
}

async function createTask() {
    if (!isLoggedIn) {
        alert("Please login or sign up first");
        return;
    }

    const response = await apiFetch("/task", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title: document.getElementById("title").value,
            description: document.getElementById("description").value,
            priority: document.getElementById("priority").value
        })
    });

    const data = await response.json();
    alert(data.message);

    document.getElementById("title").value = "";
    document.getElementById("description").value = "";
    document.getElementById("priority").value = "medium";

    loadTasks();
    loadAnalytics();
}

async function loadTasks() {
    if (!isLoggedIn) {
        return;
    }

    const response = await apiFetch("/tasks");
    allTasks = await response.json();

    renderTasks();
}

function renderTasks() {
    const table = document.getElementById("tasks");
    table.innerHTML = "";

    const searchText = document.getElementById("searchInput")?.value.toLowerCase() || "";
    const priorityFilter = document.getElementById("priorityFilter")?.value || "all";
    const statusFilter = document.getElementById("statusFilter")?.value || "all";

    const filteredTasks = allTasks.filter(task => {
        const matchesSearch =
            task.title.toLowerCase().includes(searchText) ||
            (task.description || "").toLowerCase().includes(searchText);

        const matchesPriority =
            priorityFilter === "all" || task.priority === priorityFilter;

        const matchesStatus =
            statusFilter === "all" || task.status === statusFilter;

        return matchesSearch && matchesPriority && matchesStatus;
    });

    if (filteredTasks.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    No tasks found
                </td>
            </tr>
        `;
        return;
    }

    filteredTasks.forEach(task => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${escapeHtml(task.title)}</td>
            <td>${escapeHtml(task.description || "")}</td>
            <td>${priorityBadge(task.priority)}</td>
            <td>${statusBadge(task.status)}</td>
            <td>
                <button class="btn btn-sm btn-success me-1" onclick="completeTask(${task.id})">
                    Complete
                </button>

                <button class="btn btn-sm btn-warning me-1" onclick="editTask(${task.id}, '${escapeForJs(task.title)}', '${escapeForJs(task.description || "")}', '${escapeForJs(task.priority)}')">
                    Edit
                </button>

                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">
                    Delete
                </button>
            </td>
        `;

        table.appendChild(row);
    });
}

async function completeTask(taskId) {
    const response = await apiFetch(`/task/${taskId}/complete`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"}
    });

    const data = await response.json();
    alert(data.message);

    loadTasks();
    loadAnalytics();
}

async function editTask(taskId, currentTitle, currentDescription, currentPriority) {
    const newTitle = prompt("Edit task title:", currentTitle);
    if (newTitle === null) return;

    const newDescription = prompt("Edit description:", currentDescription);
    if (newDescription === null) return;

    const newPriority = prompt("Edit priority: low / medium / high", currentPriority);
    if (newPriority === null) return;

    const response = await apiFetch(`/task/${taskId}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title: newTitle,
            description: newDescription,
            priority: newPriority
        })
    });

    const data = await response.json();
    alert(data.message);

    loadTasks();
    loadAnalytics();
}

async function deleteTask(taskId) {
    if (!confirm("Are you sure you want to delete this task?")) {
        return;
    }

    const response = await apiFetch(`/task/${taskId}`, {
        method: "DELETE",
        headers: {"Content-Type": "application/json"}
    });

    const data = await response.json();
    alert(data.message);

    loadTasks();
    loadAnalytics();
}

async function loadAnalytics() {
    const dauResponse = await apiFetch("/analytics/dau");
    const dau = await dauResponse.json();

    const tasksResponse = await apiFetch("/analytics/tasks-created");
    const tasks = await tasksResponse.json();

    const rateResponse = await apiFetch("/analytics/completion-rate");
    const rate = await rateResponse.json();

    document.getElementById("dau").innerText = dau.daily_active_users;
    document.getElementById("tasksCreated").innerText = tasks.tasks_created;
    document.getElementById("completionRate").innerText = rate.completion_rate + "%";
}

function priorityBadge(priority) {
    if (priority === "high") {
        return `<span class="badge bg-danger">High</span>`;
    }

    if (priority === "medium") {
        return `<span class="badge bg-warning text-dark">Medium</span>`;
    }

    return `<span class="badge bg-success">Low</span>`;
}

function statusBadge(status) {
    if (status === "completed") {
        return `<span class="badge bg-success">Completed</span>`;
    }

    return `<span class="badge bg-secondary">Open</span>`;
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeForJs(text) {
    return String(text)
        .replaceAll("\\", "\\\\")
        .replaceAll("'", "\\'")
        .replaceAll("\n", "\\n")
        .replaceAll("\r", "");
}

// Restore the login state from the backend session when the page loads.
checkSession();

// Load analytics when the page starts.
// These endpoints are public and do not require user authentication.
loadAnalytics();