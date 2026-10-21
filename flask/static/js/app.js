// Minimal client for the JSON API. The token lives in sessionStorage and
// travels only in the Authorization header: the browser never attaches it
// on its own, the way it would with a cookie.
const TOKEN_KEY = "access_token";
const $ = (id) => document.getElementById(id);
// ---------------------------------------------------------------- token
function getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
    if (token) sessionStorage.setItem(TOKEN_KEY, token);
    else sessionStorage.removeItem(TOKEN_KEY);
}
// Read the payload to show who is signed in and when the token expires.
// This does NOT verify the signature: only the server can, and it does on
// every request.
function payload() {
    const token = getToken();
    if (!token) return null;
    try {
        const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        return JSON.parse(atob(part));
    } catch {
        return null;
    }
}
// ---------------------------------------------------------------- API
async function api(path, { method = "GET", body } = {}) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    const res = await fetch(path, { method, headers, body: body && JSON.stringify(body) });
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && token) {
        setToken(null); // expired or invalid: back to the login form
        render();
    }

    if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
    return data;
}
// ---------------------------------------------------------------- views
function show(message, kind = "error") {
    const box = $("message");
    box.textContent = message;
    box.className = `flash flash-${kind}`;
    box.hidden = !message;
}
// Run an async action and show its error, if any.
async function run(action) {
    show("");
    try {
        await action();
    } catch (err) {
        show(err.message);
    }
}

async function render() {
    const user = payload();
    const signedIn = Boolean(user) && user.exp * 1000 > Date.now();
    if (!signedIn) setToken(null);

    $("auth-view").hidden = signedIn;
    $("todos-view").hidden = !signedIn;
    $("logout").hidden = !signedIn;
    $("who").textContent = signedIn ? user.username : "";

    if (signedIn) await loadTodos();
}

async function loadTodos() {
    const { todos } = await api("/api/todos");
    $("todo-list").replaceChildren(...todos.map(todoItem));
    $("count").textContent = `(${todos.length})`;
    $("empty").hidden = todos.length > 0;
}
// A button that calls the API and then reloads the list.
// If the action returns nothing (the user cancelled), nothing is reloaded.
function button(text, className, action) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = className;
    b.textContent = text;
    b.addEventListener("click", () => run(async () => {
        if (await action()) await loadTodos();
    }));
    return b;
}
// Built with textContent, never innerHTML: a title such as
// <img src=x onerror=...> is shown as text instead of running.
function todoItem(todo) {
    const li = document.createElement("li");
    li.className = "todo-item" + (todo.completed ? " completed" : "");

    const check = button(todo.completed ? "✔" : "", "checkbox", () =>
        api(`/api/todos/${todo.id}`, { method: "PATCH", body: { completed: !todo.completed } }));
    check.setAttribute("aria-label", "Toggle completed");
    
    const body = document.createElement("div");
    body.className = "todo-body";

    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;
    body.append(title);

    if (todo.description) {
        const description = document.createElement("p");
        description.className = "todo-description";
        description.textContent = todo.description;
        body.append(description);
    }
    
    const actions = document.createElement("div");
    actions.className = "todo-actions";
    actions.append(button("Edit", "btn btn-small", () => {
        const newTitle = prompt("New title", todo.title);
        return newTitle && api(`/api/todos/${todo.id}`, { method: "PATCH", body: { title: newTitle }
        });
    }));
    actions.append(button("Delete", "btn btn-small btn-danger", () =>
        confirm("Delete this todo?") && api(`/api/todos/${todo.id}`, { method: "DELETE" })));

    li.append(check, body, actions);
    return li;
}
// ---------------------------------------------------------------- events
function credentials() {
    return { username: $("username").value, password: $("password").value };
}
async function signIn() {
    const { access_token } = await api("/auth/login", { method: "POST", body: credentials() });
    setToken(access_token);
    $("login-form").reset();
    await render();
}


$("login-form").addEventListener("submit", (event) => {
    event.preventDefault();
    run(signIn);
});

$("register").addEventListener("click", () => run(async () => {
    if (!$("login-form").reportValidity()) return;
    await api("/auth/register", { method: "POST", body: credentials() });
    await signIn();
    show("Account created.", "success");
}));

$("create-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const fields = event.target.elements;
    run(async () => {
        await api("/api/todos", {
            method: "POST",
            body: { title: fields.title.value, description: fields.description.value },
        });
        event.target.reset();
        await loadTodos();
    });
});
// Logging out is forgetting the token. The server keeps no session to close.
$("logout").addEventListener("click", () => {
    setToken(null);
    render();
    show("Signed out.", "success");
});


run(render);