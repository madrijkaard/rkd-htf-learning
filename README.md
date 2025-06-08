# rkd-htf-learning

Projeto responsável por capturar, armazenar e visualizar métricas de livro de ofertas (order book) da Binance para uso no núcleo de aprendizado do sistema [`rkd-htf-core`](https://github.com/madrijkaard/rkd-htf-core).  
O sistema expõe APIs FastAPI para captura automatizada, análise e visualização dos dados.

---

## 📐 Visão geral da arquitetura

- **FastAPI**: expõe endpoints REST e serve páginas interativas (docs/heatmap).
- **Coleta de dados**: agendamento da captura do livro de ofertas (order book) de símbolos configuráveis da Binance.
- **Armazenamento**: dados salvos em arquivos CSV para posterior análise/modelagem.
- **Visualização**: geração de heatmaps interativos via Plotly.js para análise visual dos dados de bids/asks.

---

## 🚀 Tecnologias utilizadas

- [FastAPI](https://fastapi.tiangolo.com/) – framework web moderno e assíncrono
- [Pandas](https://pandas.pydata.org/) – manipulação de dados
- [Plotly.js](https://plotly.com/javascript/) – visualização de heatmaps no navegador
- [Uvicorn](https://www.uvicorn.org/) – servidor ASGI leve
- [Jinja2](https://jinja.palletsprojects.com/) – templates HTML

---

## 📁 Estrutura do projeto

```
rkd-htf-learning/
├── app/
│   ├── main.py                  # ponto de entrada da API
│   ├── routers/                 # endpoints organizados
│   │   ├── candlestick.py
│   │   ├── learning.py
│   │   └── order_book.py
│   ├── schemas/                 # modelos de dados (Pydantic)
│   ├── services/                # lógica de negócio (coleta, heatmap)
│   ├── schedules/               # agendadores (ex: order_book a cada 60s)
│   ├── templates/               # HTML Jinja2 para visualização Plotly.js
│   └── config/                  # settings e leitura do .env
├── data/
│   ├── bids/                    # arquivos CSV de ordens de compra
│   └── asks/                    # arquivos CSV de ordens de venda
├── static/                      # recursos estáticos para frontend
├── .env                         # variáveis de ambiente
├── requirements.txt             # dependências Python
├── Dockerfile                   # imagem Docker para deploy
└── README.md                    # este arquivo
```

---

## ⚙️ Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/madrijkaard/rkd-htf-learning.git
cd rkd-htf-learning
```

### 2. Crie e ative um ambiente virtual

**Linux/macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```
**Windows**
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure seu `.env`

Crie um arquivo `.env` na raiz:
```env
APP_NAME=rkd-htf-learning
SYMBOL=BTCUSDT
```
- `SYMBOL`: define o par de criptoativo para captura do order book (ex: BTCUSDT).

### 5. Execute o servidor

```bash
uvicorn app.main:app --reload
```

Acesse em: [http://localhost:8000](http://localhost:8000)

---

## 🐳 Executando com Docker

### 1. Construa a imagem Docker

```bash
docker build -t rkd-htf-learning .
```

### 2. Execute em background

```bash
docker run -d -p 8000:8000 --name rkd-container rkd-htf-learning
```

O sistema automaticamente faz um POST para iniciar a captura após 20 segundos:
```
POST http://localhost:8000/order-books/capture/start
```

### 3. Acesse a aplicação

- Documentação OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 🛑 Parar e remover o container

```bash
docker stop rkd-container
docker rm rkd-container
```

---

## 📊 Endpoints principais

> Os endpoints usam o prefixo plural, conforme as rotas do FastAPI.

- **POST `/order-books/capture/start`**  
  Inicia o agendador para capturar automaticamente o order book a cada 60 segundos.

- **POST `/order-books/capture/stop`**  
  Interrompe o agendador de captura.

- **GET `/order-books/capture/status`**  
  Retorna o status do agendador.

- **GET `/order-books/heatmap?symbol=BTCUSDT`**  
  Renderiza um heatmap interativo dos dados de bids/asks do símbolo.

- **GET `/candlesticks/`**  
  Endpoints para candles (exemplo: OHLCV de ativos).

- **GET `/learnings/`**  
  Endpoints para uso futuro relacionados a aprendizado.

Acesse a documentação interativa em `/docs` para explorar todas as rotas.

---

## 📈 Exemplo de visualização

O heatmap gerado compara os volumes de ordens de compra (`bids`) e venda (`asks`) por preço ao longo do tempo.

> Para gerar um heatmap válido, certifique-se de acionar o endpoint `/order-books/capture/start` e aguardar a captura de dados.

---

## 📌 To-do (sugestões futuras)

- [ ] Suporte a múltiplos `symbols` dinâmicos
- [ ] Persistência em banco de dados
- [ ] Treinamento de modelos de aprendizado com os dados
- [ ] Interface para visualização histórica

---

## 🧪 Testes

No momento os testes são manuais. Para automação, recomenda-se:

```bash
pip install pytest httpx
```

---

## 📄 Licença

MIT © [madrijkaard](https://github.com/madrijkaard)