from flask import Flask
from flask import request
from flask import render_template_string
from flask import session
from flask import jsonify
import socket


app = Flask(__name__)
app.secret_key = ''

PORT = 8899

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Printer Control</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        * { box-sizing: border-box; }

        body {
            font-family: 'Inter', sans-serif;
            background: #f4f7fc;
            margin: 0; padding: 20px;
            color: #333;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h2 {
            font-weight: 600;
            margin-bottom: 1rem;
            color: #222;
        }

        form.connect-form {
            background: white;
            padding: 20px 25px;
            border-radius: 10px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 10px;
            max-width: 360px;
            width: 100%;
        }

        form.connect-form input[type="text"] {
            flex-grow: 1;
            padding: 10px 14px;
            border: 1.8px solid #ccc;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        form.connect-form input[type="text"]:focus {
            border-color: #5c7cfa;
            outline: none;
        }

        form.connect-form button {
            background-color: #5c7cfa;
            color: white;
            border: none;
            padding: 11px 20px;
            font-weight: 600;
            font-size: 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        form.connect-form button:hover {
            background-color: #4a65d9;
        }

        p.error-text {
            color: #e03e3e;
            margin-bottom: 1rem;
            font-weight: 600;
        }

        .draggable {
            position: absolute;
            width: 90vw;
            max-width: 800px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            overflow: auto;
            user-select: none;
            cursor: grab;
            padding: 10px;
        }

        .draggable:active {
            cursor: grabbing;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 10px;
        }

        th, td {
            padding: 14px 18px;
            text-align: center;
            font-size: 1rem;
            border-bottom: 1px solid #f0f0f0;
            height: 100%;
            vertical-align: middle;
        }

        th {
            background: #5c7cfa;
            color: white;
            font-weight: 600;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:nth-child(even) td {
            background: #fafbff;
        }

        td:first-child {
            font-weight: 600;
            color: #555;
        }

        .control-buttons form {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .control-buttons button {
            background-color: #5c7cfa;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s ease;
            min-width: 90px;
        }

        .control-buttons button:hover {
            background-color: #4a65d9;
        }

        p.status-text {
            max-width: 800px;
            font-weight: 500;
            color: #666;
            text-align: center;
            margin-top: 20px;
        }

        @media (max-width: 600px) {
            .draggable {
                width: 95vw;
                max-width: none;
            }

            th, td {
                padding: 10px 8px;
                font-size: 0.9rem;
            }

            .control-buttons button {
                min-width: 70px;
                padding: 8px 12px;
                font-size: 0.9rem;
            }
        }
        iframe {
            width: 100%;
            height: 100vh;
            position: relative;
            z-index: -1;
        }

    </style>
</head>
<body>
    <!--iframe src = "http://192.168.68.45:8080/?action=stream"></iframe-->
    <h2 style = "z-index: 0; ">Printer Control</h2>

    {% if not connected %}
        <p class="error-text">{{ text }}</p>
        <form method="get" action="{{ url_for('control') }}" class="connect-form" autocomplete="off">
            <input type="text" name="ip" placeholder="Enter Printer IP" value="{{ ip or '' }}" required />
            <button type="submit">Connect
            </button>

        </form>
    {% else %}
        <div
          class="draggable" id="draggable" style="left: {{ left }}px; top: {{ top }}px;"
        >
            <table>

    <thead>
        <tr>
            <th colspan="3">Temperature</th>
            <th colspan="2">Progress</th>

            <th>Control</th>
        </tr>
        <tr>
            <th>Part</th>
            <th>SET</th>
            <th>NOW</th>

            <th>Label</th>
            <th>Value</th>

            <th>Status</th>
        </tr>

    </thead>
    <tbody>
        <tr>
            <td>HOTEND</td>
            <td id="temp_set_he">{{ temp_set_he }} °C</td>
            <td id="temp_now_he">{{ temp_now_he }} °C</td>
            <td>Done:</td>

            <td id="progress_done">{{ progress_done }} %</td>
            <td></td>

        </tr>
        <tr>
            <td>BED</td>
            <td id="temp_set_bed">{{ temp_set_bed }} °C</td>
            <td id="temp_now_bed">{{ temp_now_bed }} °C</td>

            <td>Layer:</td>
            <td id="layer">{{ layer }}</td>
            <td class="control-buttons">
                <form method="post" action="{{ url_for('control', ip=ip) }}">
                    <button type="submit" name="LED" value="SWITCH">LED</button>
                    <button type="submit" name="PAUSE" value="ON">PAUSE</button>

                    <button type="submit" name="RESUME" value="ON">RESUME</button>
                    <button type="submit" name="STOP" value="ON">CANCEL</button>
                    <button type="submit" name="HOME" value="ON">HOME</button>
                </form>
            </td>

        </tr>
        <tr>
            <td>FILE</td>
            <td colspan="2" id="file">{{ file }}</td>
            <td>State:</td>
            <td colspan="2" id="state">{{ state }}</td>

        </tr>
    </tbody>
</table>

        </div>
        <p class="status-text">{{ text }}</p>
    {% endif %}

    <script>
        const draggable = document.getElementById('draggable');

        if (draggable) {
            let isDragging = false;
            let offsetX = 0;
            let offsetY = 0;

            draggable.addEventListener('mousedown', (e) => {
                isDragging = true;
                offsetX = e.clientX - draggable.offsetLeft;
                offsetY = e.clientY - draggable.offsetTop;
                draggable.style.cursor = 'grabbing';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    let newLeft = e.clientX - offsetX;
                    let newTop = e.clientY - offsetY;
                    const maxLeft = window.innerWidth - draggable.offsetWidth;
                    const maxTop = window.innerHeight - draggable.offsetHeight;

                    if (newLeft < 0) newLeft = 0;
                    if (newTop < 0) newTop = 0;
                    if (newLeft > maxLeft) newLeft = maxLeft;
                    if (newTop > maxTop) newTop = maxTop;

                    draggable.style.left = newLeft + 'px';
                    draggable.style.top = newTop + 'px';
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    draggable.style.cursor = 'grab';
                    fetch('{{ url_for("save_position") }}', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: JSON.stringify({
                            left: draggable.offsetLeft,
                            top: draggable.offsetTop
                        })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status !== 'ok') {
                            console.error('Failed to save position');
                        }
                    })
                    .catch(console.error);
                }
            });
        }
    </script>
    <script>
        const printerIP = "{{ ip }}";

        function fetchStatus() {
            fetch(`/get_status?ip=${printerIP}`)
                .then(res => res.json())
                .then(data => {
                    if (data.error) return;

                    document.getElementById('temp_set_he').textContent = `${data.temp_set_he} °C`;
                    document.getElementById('temp_now_he').textContent = `${data.temp_now_he} °C`;
                    document.getElementById('temp_set_bed').textContent = `${data.temp_set_bed} °C`;
                    document.getElementById('temp_now_bed').textContent = `${data.temp_now_bed} °C`;
                    document.getElementById('progress_done').textContent = `${data.progress_done} %`;
                    document.getElementById('layer').textContent = data.layer;
                    document.getElementById('file').textContent = data.file;
                    document.getElementById('state').textContent = data.state;
                })
                .catch(console.error);
        }

        setInterval(fetchStatus, 3000);
    </script>

</body>
</html>
"""

CMD_RCM = b'~M601 S1\r\n'
CMD_RIM = b'~M115\r\n'
CMD_RTM = b'~M105\r\n'
CMD_RHM = b'~G28\r\n'
CMD_PROGRESS = b'~M27\r\n'
CMD_STATUS = b'~M119\r\n'
CMD_LED_ON = b'~M146 r255 g255 b255\r\n'
CMD_CAL = b'~M650\r\n'
CMD_PAUSE = b'~M25\r\n'
CMD_RESUME = b'~M24\r\n'
CMD_CANCEL = b'~M26\r\n'
CMD_HOME = b'~G28\r\n'


def send_command(sock, cmd):
    sock.sendall(cmd)
    return sock.recv(1024).decode(errors='ignore')


@app.route('/printer', methods=['GET', 'POST'])
def control():
    ip = request.args.get('ip')
    if not ip:
        return render_template_string(HTML_TEMPLATE, connected=False, text="Please enter printer IP.", ip=ip,
                                      left=50, top=100)

    text = ""
    connected = False
    temp_set_he = temp_now_he = temp_set_bed = temp_now_bed = progress_done = layer = file = state = ""

    left = session.get('draggable_left', 50)
    top = session.get('draggable_top', 100)

    try:
        with socket.create_connection((ip, PORT), timeout=2) as sock:
            connected = True
            text = f"Connection successful on IP {ip}, port {PORT}"

            send_command(sock, CMD_RCM)

            if request.method == 'POST':
                form = request.form
                if form.get('LED') == 'SWITCH':
                    send_command(sock, CMD_LED_ON)
                if form.get('PAUSE') == 'ON':
                    send_command(sock, CMD_PAUSE)
                if form.get('RESUME') == 'ON':
                    send_command(sock, CMD_RESUME)
                if form.get('STOP') == 'ON':
                    send_command(sock, CMD_CANCEL)
                if form.get('HOME') == 'ON':
                    send_command(sock, CMD_HOME)

            temp_response = send_command(sock, CMD_RTM)

            sock.sendall(CMD_PROGRESS)
            progress_response = ""
            while True:
                chunk = sock.recv(1024).decode(errors='ignore')
                progress_response += chunk
                if "ok" in chunk:
                    break

            sock.sendall(CMD_STATUS)
            status_response = ""
            while True:
                chunk = sock.recv(1024).decode(errors='ignore')
                status_response += chunk
                if "ok" in chunk:
                    break

            try:
                t0_split = temp_response.split('T0:')
                t1_split = t0_split[1].split('T1:')
                hotend = t1_split[0].strip()
                temps_he = hotend.split('/')
                temp_now_he = temps_he[0]
                temp_set_he = temps_he[1]

                b_split = t1_split[1].split('B:')
                bed_temp_part = b_split[1].split('ok')[0].strip()
                temps_bed = bed_temp_part.split('/')
                temp_now_bed = temps_bed[0]
                temp_set_bed = temps_bed[1]
            except Exception:
                temp_now_he = temp_set_he = temp_now_bed = temp_set_bed = "N/A"

            try:
                progress_parts = progress_response.split('byte')
                done_layer_part = progress_parts[1].strip()
                done, rest = done_layer_part.split('/', 1)
                progress_done = done.strip()
                layer_split = rest.split('Layer:')
                if len(layer_split) > 1:
                    layer_part = layer_split[1].split('ok')[0].strip()
                    layer = layer_part
                else:
                    layer = "N/A"
            except Exception:
                progress_done = "N/A"
                layer = "N/A"

            try:
                file_part = status_response.split('CurrentFile:')[1]
                file = file_part.split('ok')[0].strip()
            except Exception:
                file = "N/A"

            try:
                import re
                match = re.search(r"State:(.*?)\r?\n", status_response)
                if match:
                    state = match.group(1).strip()
                else:
                    state = "N/A"
            except Exception:
                state = "N/A"


    except Exception as e:
        text = f"Connection failed: {e}"
        connected = False

    return render_template_string(HTML_TEMPLATE,
                                  connected=connected,
                                  text=text,
                                  ip=ip,
                                  temp_set_he=temp_set_he,
                                  temp_now_he=temp_now_he,
                                  temp_set_bed=temp_set_bed,
                                  temp_now_bed=temp_now_bed,
                                  progress_done=progress_done,
                                  layer=layer,
                                  file=file,
                                  state=state,
                                  left=left,
                                  top=top)

@app.route('/get_status')
def get_status():
    ip = request.args.get('ip')
    if not ip:
        return jsonify(error="Missing IP"), 400

    try:
        with socket.create_connection((ip, PORT), timeout=2) as sock:
            send_command(sock, CMD_RCM)
            temp_response = send_command(sock, CMD_RTM)

            sock.sendall(CMD_PROGRESS)
            progress_response = ""
            while True:
                chunk = sock.recv(1024).decode(errors='ignore')
                progress_response += chunk
                if "ok" in chunk:
                    break

            sock.sendall(CMD_STATUS)
            status_response = ""
            while True:
                chunk = sock.recv(1024).decode(errors='ignore')
                status_response += chunk
                if "ok" in chunk:
                    break
            try:
                t0_split = temp_response.split('T0:')
                t1_split = t0_split[1].split('T1:')
                hotend = t1_split[0].strip()
                temps_he = hotend.split('/')
                temp_now_he = temps_he[0]
                temp_set_he = temps_he[1]

                b_split = t1_split[1].split('B:')
                bed_temp_part = b_split[1].split('ok')[0].strip()
                temps_bed = bed_temp_part.split('/')
                temp_now_bed = temps_bed[0]
                temp_set_bed = temps_bed[1]
            except:
                temp_now_he = temp_set_he = temp_now_bed = temp_set_bed = "N/A"

            try:
                progress_parts = progress_response.split('byte')
                done_layer_part = progress_parts[1].strip()
                done, rest = done_layer_part.split('/', 1)
                progress_done = done.strip()
                layer_split = rest.split('Layer:')
                layer = layer_split[1].split('ok')[0].strip() if len(layer_split) > 1 else "N/A"
            except:
                progress_done = layer = "N/A"

            try:
                file = status_response.split('CurrentFile:')[1].split('ok')[0].strip()
            except:
                file = "N/A"
            try:
                file = status_response.split('Status:')[1].split('ok')[0].strip()
            except Exception:
                state = "N/A"



            return jsonify(
                temp_now_he=temp_now_he,
                temp_set_he=temp_set_he,
                temp_now_bed=temp_now_bed,
                temp_set_bed=temp_set_bed,
                progress_done=progress_done,
                layer=layer,
                file=file,
                state=state
            )
    except Exception as e:
        return jsonify(error=str(e)), 500



@app.route('/save_position', methods=['POST'])
def save_position():
    if request.is_json:
        data = request.get_json()
        left = int(data.get('left', 50))
        top = int(data.get('top', 100))

        session['draggable_left'] = left
        session['draggable_top'] = top

        return jsonify(status='ok')
    return jsonify(status='fail'), 400


if __name__ == '__main__':
    app.run()
        
