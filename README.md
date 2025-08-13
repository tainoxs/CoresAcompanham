# Screen Color to QLC+ (Art-Net Ambilight)

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Este projeto cria um efeito de "ambilight" sincronizando luzes controladas pelo QLC+ com o conteúdo da sua tela. Ele captura a cor predominante de uma área específica do monitor, a processa e a envia em tempo real para o QLC+ através do protocolo Art-Net.

## Funcionalidades

- **Captura de Cor em Tempo Real**: Captura a cor média de uma região customizável da tela.
- **Comunicação via Art-Net**: Envia os dados de cor RGB para o QLC+ ou qualquer software compatível.
- **Pré-visualização ao Vivo**: Mostra uma janela com a área de captura e a cor RGB final que está sendo enviada.
- **Ajustes Finos de Cor**:
  - **Suavização de Transição**: Evita mudanças de cor bruscas.
  - **Ajuste de Brilho e Saturação**: Permite realçar ou atenuar a cor capturada.
  - **Ganhos de Cor (RGB)**: Controle individual para os canais Vermelho, Verde e Azul.
  - **Normalização de Brilho**: Garante que a cor utilize o máximo de brilho possível, evitando cores "lavadas".
- **Configuração Simples**: Todos os parâmetros importantes são facilmente ajustáveis no início do script.

## Pré-requisitos

- Python 3.x
- QLC+ (ou outro software de controle de iluminação que aceite Art-Net).

## Instalação

1.  **Clone o repositório** (ou simplesmente baixe os arquivos):
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DA_PASTA>
    ```

2.  **Instale as dependências** necessárias via pip:
    ```bash
    pip install mss numpy opencv-python
    ```

## Como Usar

### 1. Configure o Script (`main.py`)

Abra o arquivo `main.py` e ajuste os seguintes parâmetros conforme sua necessidade:

-   `QLC_IP`: O endereço IP da máquina onde o QLC+ está rodando. Use `"127.0.0.1"` se for na mesma máquina.
-   `sct.monitors[2]`: Selecione o monitor a ser capturado. `[1]` é o primeiro monitor, `[2]` o segundo, e assim por diante. Use `[0]` para capturar de todos os monitores combinados.
-   `region` (`width`, `height`): Defina a largura e altura da área de captura no centro do monitor.

#### Ajustes Finos (Opcional)

-   `SMOOTHING_FACTOR`: Um valor entre `0.0` e `1.0`. Valores menores criam transições de cor mais suaves e lentas.
-   `BRIGHTNESS_GAIN`: Adiciona um valor de brilho (0-255) à cor capturada.
-   `SATURATION_FACTOR`: Altera a intensidade da cor. `1.0` é normal, `> 1.0` deixa a cor mais vibrante.
-   `R_GAIN`, `G_GAIN`, `B_GAIN`: Multiplicadores para ajustar a intensidade de cada canal de cor individualmente.

### 2. Configure o QLC+

-   **Habilite a Entrada Art-Net**:
    1.  Vá para a aba **Entradas/Saídas**.
    2.  Selecione o universo que deseja usar (ex: `Universo 1`).
    3.  Marque a caixa de seleção **Entrada** e escolha a opção `ArtNet`.
-   **Crie um Fixture RGB**:
    1.  Vá para a aba **Fixtures**.
    2.  Adicione um fixture simples, como um `Generic RGB Panel`.
    3.  Configure o endereço DMX para corresponder ao que o script envia (Universo 1, Endereço 1).

### 3. Execute o Script

Abra um terminal na pasta do projeto e execute:

```bash
python main.py
```

-   Uma janela chamada **`Captured Area`** aparecerá, mostrando a pré-visualização.
-   Para parar o script, pressione a tecla **`q`** com a janela de pré-visualização em foco.

## Contribuições

Sinta-se à vontade para abrir uma *issue* para relatar problemas ou sugerir melhorias. *Pull requests* são bem-vindos!