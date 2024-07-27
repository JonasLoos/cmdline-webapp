import streamlit as st
import subprocess
import threading
import queue

def run_command(command, output_queue):
  try:
      result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
      output_queue.put(f"Command executed successfully:\n{result.stdout}")
  except subprocess.CalledProcessError as e:
      output_queue.put(f"Error executing command:\n{e.stderr}")

def main():
  st.title("ROS2 Web Interface")

  # Sidebar for adding custom buttons and sliders
  st.sidebar.header("Custom Controls")
  if st.sidebar.button("Add Button"):
      st.session_state.setdefault('custom_buttons', []).ap<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROS2 Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #chat { height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }
        #command-input { width: 70%; }
        button { margin: 5px; }
        .ui-element { margin: 10px 0; }
        .ui-element button { margin-left: 10px; }
    </style>
</head>
<body>
    <h1>ROS2 Web Interface</h1>
    <div id="chat"></div>
    <input type="text" id="command-input" placeholder="Enter command">
    <button onclick="sendCommand()">Send Command</button>
    <button onclick="addUIElement()">Add UI Element</button>
    <button onclick="viewLog()">View Log</button>
    <div id="ui-elements"></div>

    <script>
        function sendCommand() {
            const command = document.getElementById('command-input').value;
            fetch('/send_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            })
            .then(response => response.json())
            .then(data => {
                appendToChatLog(`Command sent: ${command}`);
                document.getElementById('command-input').value = '';
            })
            .catch((error) => {
                console.error('Error:', error);
                appendToChatLog(`Error sending command: ${error}`);
            });
        }

        function addUIElement() {
            const command = document.getElementById('command-input').value;
            const elementType = prompt("Enter element type (button/slider):");
            if (elementType === 'button' || elementType === 'slider') {
                const element = document.createElement('div');
                element.className = 'ui-element';
                if (elementType === 'button') {
                    element.innerHTML = `<button onclick="executeCommand('${command}')">${command}</button>`;
                } else {
                    element.innerHTML = `<input type="range" min="0" max="100" value="50" oninput="executeCommand('${command} ' + this.value)"><span>${command}</span>`;
                }
                element.innerHTML += `<button onclick="editElement(this)">Edit</button><button onclick="deleteElement(this)">Delete</button>`;
                document.getElementById('ui-elements').appendChild(element);
            }
        }

        function executeCommand(command) {
            fetch('/send_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command: command }),
            })
            .then(response => response.json())
            .then(data => {
                appendToChatLog(`Command executed: ${command}`);
            })
            .catch((error) => {
                console.error('Error:', error);
                appendToChatLog(`Error executing command: ${error}`);
            });
        }

        function editElement(button) {
            const element = button.parentElement;
            const newCommand = prompt("Enter new command:");
            if (newCommand) {
                if (element.firstChild.tagName === 'BUTTON') {
                    element.firstChild.textContent = newCommand;
                    element.firstChild.onclick = () => executeCommand(newCommand);
                } else {
                    element.querySelector('span').textContent = newCommand;
                    element.querySelector('input').oninput = () => executeCommand(newCommand + ' ' + this.value);
                }
            }
        }

        function deleteElement(button) {
            button.parentElement.remove();
        }

        function viewLog() {
            fetch('/get_log')
            .then(response => response.json())
            .then(data => {
                data.forEach(log => {
                    appendToChatLog(`${log.status.toUpperCase()}: ${log.output}`);
                });
            })
            .catch((error) => {
                console.error('Error:', error);
                appendToChatLog(`Error fetching log: ${error}`);
            });
        }

        function appendToChatLog(message) {
            const chat = document.getElementById('chat');
            chat.innerHTML += `<p>${message}</p>`;
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>pend({
          'name': st.sidebar.text_input(f"Button {len(st.session_state.get('custom_buttons', [])) + 1} Name"),
          'command': st.sidebar.text_input(f"Button {len(st.session_state.get('custom_buttons', [])) + 1} Command")
      })

  if st.sidebar.button("Add Slider"):
      st.session_state.setdefault('custom_sliders', []).append({
          'name': st.sidebar.text_input(f"Slider {len(st.session_state.get('custom_sliders', [])) + 1} Name"),
          'command': st.sidebar.text_input(f"Slider {len(st.session_state.get('custom_sliders', [])) + 1} Command"),
          'min': st.sidebar.number_input(f"Slider {len(st.session_state.get('custom_sliders', [])) + 1} Min", value=0),
          'max': st.sidebar.number_input(f"Slider {len(st.session_state.get('custom_sliders', [])) + 1} Max", value=100)
      })

  # Custom buttons
  for i, button in enumerate(st.session_state.get('custom_buttons', [])):
      if st.button(button['name'], key=f"custom_button_{i}"):
          command_queue.put(button['command'])

  # Custom sliders
  for slider in st.session_state.get('custom_sliders', []):
      value = st.slider(slider['name'], min_value=slider['min'], max_value=slider['max'])
      if st.button(f"Send {slider['name']}"):
          command_queue.put(f"{slider['command']} {value}")

  # Command input
  command = st.text_input("Enter ROS2 command:")
  if st.button("Execute Command"):
      command_queue.put(command)

  # Chat section
  st.header("Chat")
  if 'messages' not in st.session_state:
      st.session_state.messages = []

  for message in st.session_state.messages:
      st.text(message)

  user_message = st.text_input("Command:")
  if st.button("Send"):
      st.session_state.messages.append(f"You: {user_message}")

  # Output section
  st.header("Output")
  output_placeholder = st.empty()

  # Command execution loop
  while True:
      try:
          command = command_queue.get_nowait()
          threading.Thread(target=run_command, args=(command, output_queue)).start()
      except queue.Empty:
          pass

      try:
          output = output_queue.get_nowait()
          output_placeholder.text(output)
          st.session_state.messages.append(f"System: {output}")
      except queue.Empty:
          pass

      st.rerun()

if __name__ == "__main__":
  command_queue = queue.Queue()
  output_queue = queue.Queue()
  main()