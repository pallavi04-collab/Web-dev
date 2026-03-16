const taskInput = document.getElementById("taskInput");
const addTaskBtn = document.getElementById("addTaskBtn");
const taskList = document.getElementById("taskList");
const pendingCount = document.getElementById("pendingCount");
const completedCount = document.getElementById("completedCount");

addTaskBtn.addEventListener("click", addTask);

function addTask() {
    const text = taskInput.value.trim();

    if (text === "") {
        alert("Please enter a task!");
        return;
    }

    const li = document.createElement("li");

    const left = document.createElement("div");
    left.className = "task-left";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";

    const span = document.createElement("span");
    span.textContent = text;

    checkbox.addEventListener("change", () => {
        span.classList.toggle("completed");
        updateCounts();
    });

    left.appendChild(checkbox);
    left.appendChild(span);

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.className = "edit-btn";

    editBtn.addEventListener("click", () => {
        const updated = prompt("Edit Task:", span.textContent);
        if (updated && updated.trim() !== "") {
            span.textContent = updated.trim();
        }
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.className = "delete-btn";

    deleteBtn.addEventListener("click", () => {
        li.style.opacity = "0";
        setTimeout(() => {
            li.remove();
            updateCounts();
        }, 300);
    });

    li.appendChild(left);
    li.appendChild(editBtn);
    li.appendChild(deleteBtn);

    taskList.appendChild(li);

    taskInput.value = "";
    updateCounts();
}

function updateCounts() {
    const tasks = taskList.querySelectorAll("li");
    const completed = taskList.querySelectorAll("input:checked").length;

    pendingCount.textContent = tasks.length - completed;
    completedCount.textContent = completed;
}
