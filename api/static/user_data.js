/*
This function handles user data submission.
*/
document.getElementById('upload-form').onsubmit = function (event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    fetch('/predict', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Dynamically create new element for task.
        const taskId = data.task_id;
        const taskContainer = document.createElement('div');
        taskContainer.id = `task-${taskId}`;
        taskContainer.innerHTML = `
            <h3>Task ID: ${taskId}</h3>
            <div>Status: <span id="status-${taskId}">Processing...</span></div>
            <div>Result: <pre id="result-${taskId}">Waiting for results...</pre></div>
        `;
        document.getElementById('task-result').appendChild(taskContainer);
        checkStatus(taskId);
    })
    .catch(error => console.error('Error:', error));
};

/*
This function continuously checks the status of the task.
*/
function checkStatus(taskId) {
    fetch(`/status/${taskId}`)
        .then(response => response.json())
        .then(statusData => {
            document.getElementById(`status-${taskId}`).innerText = statusData.status;
            if (statusData.status === 'completed') {
                fetchResults(taskId);
            } else if (statusData.status.startsWith('failed')) {
                document.getElementById(`result-${taskId}`).innerText = `Error: ${statusData.status}`;
            } else {
                setTimeout(() => checkStatus(taskId), 1000);
            }
        });
}

/*
This function fetches the task results from the 'database', which in this case is just a dictionary created in main.py.
*/
function fetchResults(taskId) {
    fetch(`/results/${taskId}`)
        .then(response => response.json())
        .then(resultData => {
            document.getElementById(`result-${taskId}`).innerText = JSON.stringify(resultData, null, 2);
        });
}


