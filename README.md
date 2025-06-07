
# rkd-htf-learning

Projeto responsável por capturar, armazenar e visualizar métricas de livro de ofertas (order book) a partir da Binance para uso no núcleo de aprendizado do sistema `rkd-htf-core`.

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
│   ├── services/                # lógica de negócio (coleta, CSV, etc.)
│   ├── schedules/               # agendadores (ex: order_book a cada 60s)
│   ├── templates/               # HTML Jinja2 para visualização Plotly.js
│   └── config/                  # settings com leitura do .env
├── data/
│   ├── bids/                    # arquivos CSV de ordens de compra
│   └── asks/                    # arquivos CSV de ordens de venda
├── static/                      # recursos estáticos para frontend (se necessário)
├── .env                         # variáveis de ambiente
├── requirements.txt             # dependências Python
└── README.md                    # este arquivo
```

---

## ⚙️ Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/rkd-htf-learning.git
cd rkd-htf-learning
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure seu `.env`

```env
APP_NAME=rkd-htf-learning
SYMBOL=BTCUSDT
```

### 5. Execute o servidor

```bash
uvicorn app.main:app --reload
```

Acesse em: [http://localhost:8000](http://localhost:8000)

---

## 🐳 Executando com Docker

Se preferir rodar o sistema em container, siga os passos abaixo:

### 1. Construa a imagem Docker

```bash
docker build -t rkd-htf-learning .
```

### 2. Execute em background

```bash
docker run -d -p 8000:8000 --name rkd-container rkd-htf-learning
```

Após aproximadamente 10 segundos, o sistema faz automaticamente um POST para iniciar a captura do livro de ofertas:

```
POST http://localhost:8000/order-book/capture/start
```

### 3. Acesse a aplicação

Abra no navegador:

[http://localhost:8000/docs](http://localhost:8000/docs)

### 🛑 Parar e remover o container

```bash
docker stop rkd-container
docker rm rkd-container
```

---

## 📊 Endpoints disponíveis

### 🔹 `/order-book/capture`  
Captura o order book da Binance para o símbolo definido no `.env` e salva os arquivos `bids/XXX.csv` e `asks/XXX.csv`.

### 🔹 `/order-book/capture/start`  
Inicia o agendador para capturar automaticamente a cada 60 segundos.

### 🔹 `/order-book/capture/stop`  
Interrompe o agendador.

### 🔹 `/heatmap`  
Renderiza no navegador um heatmap interativo com base nos arquivos `data/bids/BTC.csv` e `data/asks/BTC.csv`.

---

## 📈 Exemplo de visualização

O heatmap gerado compara os volumes de ordens de compra (`bids`) e venda (`asks`) por preço, usando um mapa de calor baseado em Plotly.js:

> Para gerar um heatmap válido, certifique-se de ter rodado o endpoint `/order-book/capture`.

---

## 📌 To-do (sugestões futuras)

- [ ] Suporte a múltiplos `symbols` dinâmicos
- [ ] Persistência em banco de dados
- [ ] Treinamento de modelos de aprendizado com os dados
- [ ] Interface para visualização histórica

---

## 🧪 Testes

Por enquanto, os testes são manuais. Para automatização, considere usar:

```bash
pip install pytest httpx
```

---

## 📄 Licença

MIT © [Seu Nome ou Organização]