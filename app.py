from flask import Flask, request, jsonify, send_file
import subprocess
import threading
import os
import uuid
import time
import signal


current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, 'static')

app = Flask(__name__, static_folder=static_folder)

command_status = {}
command_output = {}
command_processes = {}


def execute_command(command_id, command):
    try:
        command_status[command_id] = "running"
        command_output[command_id] = ""
        
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid)
        command_processes[command_id] = process

        while True:
            if command_status[command_id] == "stopped":
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                command_output[command_id] += "\nCommand stopped by user."
                break
            
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                command_output[command_id] += output.strip() + "\n"

        _, stderr = process.communicate()

        if command_status[command_id] != "stopped":
            if process.returncode == 0:
                command_status[command_id] = "completed"
            else:
                command_status[command_id] = "failed"
                if stderr.strip():
                    command_output[command_id] += f"Error Output:\n{stderr}"

        del command_processes[command_id]
        return {"id": command_id, "status": command_status[command_id], "output": command_output[command_id]}
    except Exception as e:
        command_status[command_id] = "failed"
        command_output[command_id] += f"\nException: {str(e)}"
        return {"id": command_id, "status": "error", "output": command_output[command_id]}


@app.route('/')
def index():
    return send_file(os.path.join(static_folder, 'index.html'))


@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json['command']
    command_id = str(uuid.uuid4())
    command_status[command_id] = "queued"
    command_output[command_id] = ""
    threading.Thread(target=execute_command, args=(command_id, command), daemon=True).start()
    time.sleep(0.03)
    return jsonify({"status": command_status[command_id], "id": command_id, "output": command_output[command_id]})


@app.route('/get_status', methods=['POST'])
def get_status():
    command_id = request.json['id']
    status = command_status.get(command_id, "unknown")
    output = command_output.get(command_id, "")
    return jsonify({"id": command_id, "status": status, "output": output})


@app.route('/stop_command', methods=['POST'])
def stop_command():
    command_id = request.json['id']
    if command_id in command_processes:
        command_status[command_id] = "stopped"
        return jsonify({"status": "stopping", "id": command_id})
    else:
        return jsonify({"status": "not_found", "id": command_id})


if __name__ == '__main__':
    print(f"Static folder path: {static_folder}")
    print(f"Index file path: {os.path.join(static_folder, 'index.html')}")
    app.run(debug=True)
