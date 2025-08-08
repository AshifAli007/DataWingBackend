import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

STORAGE_DIR = "/home/ashif"

app = Flask(__name__)
CORS(app)



def safe_join(base, *paths):
    # Prevent path traversal attacks
    new_path = os.path.abspath(os.path.join(base, *paths))
    if not new_path.startswith(base):
        raise ValueError("Unsafe path")
    return new_path

# List files and folders (optionally in a subdirectory)
@app.route("/files", methods=["GET"])
def list_files():
    subdir = request.args.get("path", "")
    directory = safe_join(STORAGE_DIR, subdir)
    files = []
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        files.append({
            "name": entry,
            "is_dir": os.path.isdir(path),
            "size": os.path.getsize(path) if os.path.isfile(path) else None
        })
    return jsonify(files)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# Download a file (optionally from a subdirectory)
@app.route("/files/download", methods=["GET"])
def download_file():
    subdir = request.args.get("path", "")
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400
    directory = safe_join(STORAGE_DIR, subdir)
    return send_from_directory(directory, filename, as_attachment=True)

# Upload a file (to a subdirectory)
@app.route("/files/upload", methods=["POST"])
def upload_file():
    subdir = request.args.get("path", "")
    directory = safe_join(STORAGE_DIR, subdir)
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    os.makedirs(directory, exist_ok=True)
    save_path = os.path.join(directory, file.filename)
    file.save(save_path)
    return jsonify({"message": f"{file.filename} uploaded successfully"})

# Delete a file (optionally from a subdirectory)
@app.route("/files/delete", methods=["POST"])
def delete_file():
    subdir = request.args.get("path", "")
    filename = request.json.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400
    directory = safe_join(STORAGE_DIR, subdir)
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    os.remove(file_path)
    return jsonify({"message": f"{filename} deleted"})

# (Optional) Create a new folder
@app.route("/folders/create", methods=["POST"])
def create_folder():
    subdir = request.args.get("path", "")
    folder_name = request.json.get("folder_name")
    if not folder_name:
        return jsonify({"error": "folder_name required"}), 400
    directory = safe_join(STORAGE_DIR, subdir, folder_name)
    os.makedirs(directory, exist_ok=True)
    return jsonify({"message": f"Folder {folder_name} created"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
