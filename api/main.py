import argparse
import os
import tempfile
import threading
import uuid
from flask import Flask, request, render_template, jsonify
from ml_model.model.predict import clean_validate_and_predict, TaskContext
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)


# Initialize thread pool.
executor = ThreadPoolExecutor(max_workers=5)

# To keep track of the processing status and task results.
processing_status = {}
task_results = {}

# Lock to prevent race condition errors
status_lock = threading.Lock()
task_results_lock = threading.Lock()


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Ensure the directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


@app.route("/predict", methods=["POST"])
def make_prediction():
    """
    This function makes a prediction based on the csv data delivered by the user. As the prediction 
    might take some time, it is being run on a different thread.
    """

    input_file = request.files.get('file')
    if input_file and input_file.filename.endswith('.csv'):
        # Save the file temporarily
        temp_dir = 'tmp'
        ensure_directory_exists(temp_dir)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=temp_dir)
        input_file.save(temp_file.name)

        # Generate a unique task ID to track the status
        task_id = str(uuid.uuid4())
        with status_lock:
            processing_status[task_id] = "processing"

        # Process the file in a separate thread
        context = TaskContext(
            task_id=task_id,
            status_lock=status_lock,
            processing_status=processing_status,
            task_results=task_results,
            task_results_lock=task_results_lock,
            temp_file_name=temp_file.name
        )
        executor.submit(clean_validate_and_predict, context, temp_file.name)

        return jsonify({"task_id": task_id, "msg": "File uploaded and processing started!"})

    return jsonify({"msg": "Invalid file format. Please upload a CSV file."}), 400


@app.route("/status/<task_id>", methods=["GET"])
def check_status(task_id):
    status = processing_status.get(task_id, "unknown task id")

    return jsonify({"task_id": task_id, "status": status})


@app.route("/results/<task_id>", methods=["GET"])
def get_results(task_id):
    result = task_results.get(task_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Task not found"}), 404


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the app.")
    parser.add_argument("--local", action="store_true", help="Run the app locally on 127.0.0.1")
    args = parser.parse_args()

    if args.local:
        app.run(debug=True)
    else:
        app.run(host="0.0.0.0", port=80, debug=True)
