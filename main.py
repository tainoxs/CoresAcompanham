import mss
import numpy as np
import socket
import struct
import time
import cv2

# IP do QLC+ (normalmente localhost)
QLC_IP = "127.0.0.1"
ARTNET_PORT = 6454

# AJUSTES FINOS
SMOOTHING_FACTOR = 0.1# Fator de suavização (0.0 a 1.0). Valores menores = mais suave.
BRIGHTNESS_GAIN = 0  # Valor a ser adicionado (0-255) (FICA MAIS BRANCO)
SATURATION_FACTOR = 0.8 # Fator de Saturação (1.0 = normal, >1.0 = mais saturado)
R_GAIN = 1.0 # Fator de ganho para o canal vermelho (1.0 = sem ganho)
G_GAIN = 0.95 # Fator de ganho para o canal verde (1.0 = sem ganho)
B_GAIN = 0.8 # Fator de ganho para o canal azul (1.0 = sem ganho)


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
        r = int(r_avg * R_GAIN)
        g = int(g_avg * G_GAIN)
        b = int(b_avg * B_GAIN)


        # --- NORMALIZAÇÃO DA COR ---
        # Encontra o valor máximo entre R, G e B para a normalização
        max_val = max(r, g, b)

        # Evita divisão por zero se a cor for preta (todos os canais são 0)
        if max_val > 0:
            # Calcula o fator de escala para que o canal mais brilhante atinja 255
            scale = 255.0 / max_val
            r = int(r * scale)
            g = int(g * scale)
            b = int(b * scale)

        # Garante que os valores finais estejam no intervalo 0-255
        r = (np.clip(r, 0, 255))
        g = (np.clip(g, 0, 255))
        b = (np.clip(b, 0, 255))
        # --- FIM DA NORMALIZAÇÃO ---

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

def send_artnet_dmx(sock, r, g, b):
    dmx_data = [0] * 512
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
    sock.sendto(packet, (QLC_IP, ARTNET_PORT))

if __name__ == "__main__":
    print("Iniciando captura e envio de cor para QLC+ via Art-Net...")
    print("Pressione 'q' na janela de visualização para sair.")

    # Cria o socket uma única vez
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        last_r, last_g, last_b = 0, 0, 0

        while True:
            r, g, b = get_average_color()

            # Suaviza a transição de cor
            smooth_r = int(last_r + (r - last_r) * SMOOTHING_FACTOR)
            smooth_g = int(last_g + (g - last_g) * SMOOTHING_FACTOR)
            smooth_b = int(last_b + (b - last_b) * SMOOTHING_FACTOR)

            # Garante que os valores permaneçam no intervalo 0-255
            smooth_r = np.clip(smooth_r, 0, 255)
            smooth_g = np.clip(smooth_g, 0, 255)
            smooth_b = np.clip(smooth_b, 0, 255)

            send_artnet_dmx(sock, smooth_r, smooth_g, smooth_b)
            print(f"Cor enviada: R={smooth_r} G={smooth_g} B={smooth_b}")

            last_r, last_g, last_b = smooth_r, smooth_g, smooth_b

            # Para fechar a janela de visualização pressione 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print("Script finalizado.")
