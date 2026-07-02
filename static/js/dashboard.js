let allTasks = [];
async function signup() {
    const response = await fetch("/signup", {
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

    if (data.user_id) {
        setUser(data.user_id);
        loadTasks();
        loadAnalytics();
    }
}

async function login() {
    const response = await fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: document.getElementById("login_email").value,
            password: document.getElementById("login_password").value
        })
    });

    const data = await response.json();
    alert(data.message);

    if (data.user_id) {
        setUser(data.user_id);
        loadTasks();
        loadAnalytics();
    }
}

function setUser(userId) {
    document.getElementById("user_id").value = userId;
    document.getElementById("currentUser").innerText = userId;
}

async function createTask() {
    const userId = document.getElementById("user_id").value;

    if (!userId) {
        alert("Please login or sign up first");
        return;
    }

    const response = await fetch("/task", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: Number(userId),
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
    const userId = document.getElementById("user_id").value;

    if (!userId) {
        alert("Please login or sign up first");
        return;
    }

    const response = await fetch(`/tasks/${userId}`);
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
    const userId = Number(document.getElementById("user_id").value);

    const response = await fetch(`/task/${taskId}/complete`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId})
    });

    const data = await response.json();
    alert(data.message);

    loadTasks();
    loadAnalytics();
}

async function editTask(taskId, currentTitle, currentDescription, currentPriority) {
    const userId = Number(document.getElementById("user_id").value);

    const newTitle = prompt("Edit task title:", currentTitle);
    if (newTitle === null) return;

    const newDescription = prompt("Edit description:", currentDescription);
    if (newDescription === null) return;

    const newPriority = prompt("Edit priority: low / medium / high", currentPriority);
    if (newPriority === null) return;

    const response = await fetch(`/task/${taskId}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: userId,
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
    const userId = Number(document.getElementById("user_id").value);

    if (!confirm("Are you sure you want to delete this task?")) {
        return;
    }

    const response = await fetch(`/task/${taskId}`, {
        method: "DELETE",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: userId})
    });

    const data = await response.json();
    alert(data.message);

    loadTasks();
    loadAnalytics();
}

async function loadAnalytics() {
    const dauResponse = await fetch("/analytics/dau");
    const dau = await dauResponse.json();

    const tasksResponse = await fetch("/analytics/tasks-created");
    const tasks = await tasksResponse.json();

    const rateResponse = await fetch("/analytics/completion-rate");
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

loadAnalytics();