"""
API local que recibe pedidos de AlwaysData y lanza la impresión
"""

from flask import Flask, request, jsonify
import hashlib
import uuid
import time
import json
import requests
import websocket
import os

app = Flask(__name__)

# ─── CONFIGURACIÓN ────────────────────────────────────────────
PRINTER_IP  = '192.168.0.150'
UPLOAD_URL  = f'http://{PRINTER_IP}/uploadFile/upload'
WS_URL      = f'ws://{PRINTER_IP}:3030/websocket'
API_SECRET  = 'printly_secret_123' 
GCODES_DIR  = r'C:\printly_gcodes'
# ──────────────────────────────────────────────────────────────


@app.route('/print', methods=['POST'])
def handle_print():
    # Verificar secret para seguridad básica
    secret = request.headers.get('X-Printly-Secret')
    if secret != API_SECRET:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401

    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'success': False, 'error': 'Falta filename'}), 400

    gcode_path = os.path.join(GCODES_DIR, filename)

    if not os.path.exists(gcode_path):
        return jsonify({'success': False, 'error': f'Archivo no encontrado: {filename}'}), 404

    print(f'[INFO] Imprimiendo: {filename}')

    # Paso 1: Subir gcode
    upload_ok = upload_gcode(gcode_path, filename)
    if not upload_ok:
        return jsonify({'success': False, 'error': 'Error al subir gcode'}), 500

    print(f'[INFO] Archivo subido correctamente')

    # Paso 2: Lanzar impresión
    print_ok = start_print(filename)
    if not print_ok:
        return jsonify({'success': False, 'error': 'Error al lanzar impresión'}), 500

    print(f'[INFO] Impresión lanzada correctamente')
    return jsonify({'success': True})


def upload_gcode(file_path, filename):
    with open(file_path, 'rb') as f:
        file_content = f.read()

    md5       = hashlib.md5(file_content).hexdigest()
    file_uuid = str(uuid.uuid4()).replace('-', '')
    file_size = len(file_content)

    files = {'File': (filename, file_content, 'application/octet-stream')}
    data  = {
        'TotalSize':  file_size,
        'Uuid':       file_uuid,
        'Offset':     0,
        'Check':      1,
        'S-File-MD5': md5,
    }

    try:
        response = requests.post(UPLOAD_URL, files=files, data=data, timeout=120)
        print(f'[INFO] Upload response: {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'[ERROR] Upload: {e}')
        return False


def start_print(filename):
    message = json.dumps({
        'Id': '',
        'Data': {
            'Cmd': 128,
            'Data': {
                'Filename':           '/local/' + filename,
                'StartLayer':         0,
                'Calibration_switch': 0,
                'PrintPlatformType':  1,
                'Tlp_Switch':         0,
            },
            'From':        1,
            'MainboardID': '',
            'RequestID':   str(uuid.uuid4()),
            'TimeStamp':   int(time.time() * 1000),
        }
    })

    try:
        ws = websocket.create_connection(WS_URL, timeout=10)
        ws.send(message)
        # Leer hasta recibir el ACK
        start = time.time()
        while time.time() - start < 5:
            ack = ws.recv()
            print(f'[INFO] WS message: {ack}')
            if 'Ack' in ack or '"Cmd":128' in ack:
                ws.close()
                return True
        ws.close()
        return False
    except Exception as e:
        print(f'[ERROR] WebSocket: {e}')
        return False


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    os.makedirs(GCODES_DIR, exist_ok=True)
    print(f'[INFO] API iniciada en http://localhost:5000')
    print(f'[INFO] Gcodes en: {GCODES_DIR}')
    app.run(host='0.0.0.0', port=5000)
