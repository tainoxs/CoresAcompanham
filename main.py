import mss
import numpy as np
import socket
import struct
import time

# IP do QLC+ (normalmente localhost)
QLC_IP = "127.0.0.1"
ARTNET_PORT = 6454

def get_average_color():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # tela principal
        # captura apenas um quadrado pequeno (800x800px no centro, testar depois com 1920x788 lá)
        width, height = 800, 800
        left = monitor['left'] + (monitor['width'] - width) // 2
        top = monitor['top'] + (monitor['height'] - height) // 2
        region = {'top': top, 'left': left, 'width': width, 'height': height}
        img = sct.grab(region)
        img_np = np.array(img)
        r = int(np.mean(img_np[:, :, 2]))
        g = int(np.mean(img_np[:, :, 1]))
        b = int(np.mean(img_np[:, :, 0]))
        return r, g, b

def send_artnet_dmx(r, g, b):
    dmx_data = [0]*512
    dmx_data[1] = r
    dmx_data[2] = g
    dmx_data[3] = b

    # Art-Net packet
    header = b'Art-Net\x00'              # Art-Net ID
    opcode = struct.pack('<H', 0x5000)   # OpOutput / OpDmx
    protocol = struct.pack('>H', 14)     # Protocol version
    sequence = b'\x00'
    physical = b'\x00'
    universe = struct.pack('<H', 0)      # Universe 0
    length = struct.pack('>H', len(dmx_data))
    payload = bytes(dmx_data)

    packet = header + opcode + protocol + sequence + physical + universe + length + payload

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (QLC_IP, ARTNET_PORT))

if __name__ == "__main__":
    print("Iniciando captura e envio de cor para QLC+ via Art-Net...")
    while True:
        r, g, b = get_average_color()
        send_artnet_dmx(r, g, b)
        print(f"Cor enviada: R={r} G={g} B={b}")
        time.sleep(0.1)
