# Screen Color to QLC+ via Art-Net

Este projeto captura a cor média de uma região da tela e a envia para o QLC+ via protocolo Art-Net. É útil para criar efeitos de ambilight sincronizados com o conteúdo da tela.

## Funcionalidades

- Captura a cor média de uma área específica da tela.
- Envia os valores de cor (R, G, B) para o QLC+ em tempo real.
- Utiliza o protocolo Art-Net para comunicação com o QLC+.

## Pré-requisitos

- Python 3
- QLC+ (ou outro software compatível com Art-Net)

## Instalação

1. Clone este repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DA_PASTA>
   ```

2. Instale as dependências:
   ```bash
   pip install mss numpy
   ```

## Como Usar

1. **Configure o `main.py`:**
   - `QLC_IP`: Defina o endereço IP onde o QLC+ está rodando (por padrão, `"127.0.0.1"` para a mesma máquina).
   - `sct.monitors[1]`: O `[1]` se refere ao monitor principal. Se você tiver múltiplos monitores, pode ser necessário ajustar este valor (`[0]` para todos os monitores, `[2]` para o segundo, etc.).
   - `region`: Você pode ajustar a área de captura alterando os valores de `width`, `height`, `left` e `top` na função `get_average_color`.

2. **Configure o QLC+:**
   - Crie um novo projeto no QLC+.
   - Adicione um universo e certifique-se de que a entrada Art-Net esteja habilitada para esse universo.
   - Adicione um fixture (por exemplo, um painel de LED RGB genérico) e configure os canais para corresponder aos canais DMX que o script está enviando (por padrão, canal 1 para Vermelho, 2 para Verde e 3 para Azul).

3. **Execute o script:**
   ```bash
   python main.py
   ```

O terminal exibirá as cores RGB que estão sendo enviadas para o QLC+.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.