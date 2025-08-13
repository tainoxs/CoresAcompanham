import mss
import numpy as np
import socket
import struct
import time
import cv2

# IP do QLC+ (normalmente localhost)
QLC_IP = "127.0.0.1"
ARTNET_PORT = 6454

# Fator de suavização (0.0 a 1.0). Valores menores = mais suave.
SMOOTHING_FACTOR = 0.1
# Ajuste estes valores para o brilho e saturação desejados
BRIGHTNESS_GAIN = 200  # Valor a ser adicionado (0-255)
SATURATION_FACTOR = 1.0 # Fator de Saturação (1.0 = normal, >1.0 = mais saturado)

def get_average_color():
    with mss.mss() as sct:
        monitor = sct.monitors[2]  # tela principal
        # captura apenas um quadrado pequeno (800x800px no centro, testar depois com 1920x788 lá)
        width, height = 1080, 540
        left = monitor['left'] + (monitor['width'] - width) // 2
        top = monitor['top'] + (monitor['height'] - height) // 2
        region = {'top': top, 'left': left, 'width': width, 'height': height}
        img = sct.grab(region)
        img_np = np.array(img)

        # --- AJUSTE DE BRILHO E SATURAÇÃO ---
        # Converte para HSV para ajustar brilho e saturação
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Aumenta o brilho (Value)
        v = cv2.add(v, BRIGHTNESS_GAIN)
        v = np.clip(v, 0, 255) # Garante que não ultrapasse 255

        # Aumenta a saturação (Saturation)
        s = s.astype(float)
        s = np.clip(s * SATURATION_FACTOR, 0, 255)
        s = s.astype(np.uint8)

        final_hsv = cv2.merge((h, s, v))
        img_np = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        # --- FIM DO AJUSTE ---

        # Reduz a qualidade da imagem (pixelização) para homogeneizar a cor
        height, width, _ = img_np.shape
        pixel_size = 128 # Quanto menor o valor, mais pixelado
        small_img = cv2.resize(img_np, (pixel_size, int(height * pixel_size / width)), interpolation=cv2.INTER_LINEAR)
        img_np = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_NEAREST)

        # Calcula a média de cada canal de cor
        r_avg = np.mean(img_np[:, :, 2])
        g_avg = np.mean(img_np[:, :, 1])
        b_avg = np.mean(img_np[:, :, 0])

        # Lógica condicional para multiplicar a cor dominante (REMOVIDA)
        # Agora apenas usamos a média direta da imagem já ajustada
        r = int(r_avg)
        g = int(g_avg * 0.95)
        b = int(b_avg * 0.8)

        # Adiciona o texto com os valores RGB na imagem
        text = f"RGB: ({r}, {g}, {b})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        position = (10, 30)
        font_scale = 1
        font_color = (255, 255, 255)  # Branco
        line_type = 2
        # Adiciona um contorno preto para melhor visibilidade
        cv2.putText(img_np, text, position, font, font_scale, (0, 0, 0), line_type + 2)
        cv2.putText(img_np, text, position, font, font_scale, font_color, line_type)

        # Mostra a imagem capturada com o texto
        cv2.imshow('Captured Area', img_np)
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
    last_r, last_g, last_b = 0, 0, 0
    while True:
        r, g, b = get_average_color()

        # Suaviza a transição de cor e garante que os valores não excedam 255
        smooth_r = min(255, int(last_r + (r - last_r) * SMOOTHING_FACTOR))
        smooth_g = min(255, int(last_g + (g - last_g) * SMOOTHING_FACTOR))
        smooth_b = min(255, int(last_b + (b - last_b) * SMOOTHING_FACTOR))

        send_artnet_dmx(smooth_r, smooth_g, smooth_b)
        print(f"Cor enviada: R={smooth_r} G={smooth_g} B={smooth_b}")

        last_r, last_g, last_b = smooth_r, smooth_g, smooth_b

        # Para fechar a janela de visualização pressione 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
