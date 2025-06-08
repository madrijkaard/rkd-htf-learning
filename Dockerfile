# Imagem base com Python 3.11
FROM python:3.11-slim

# Argumento para forçar invalidação de cache
ARG CACHE_BUSTER=initial

# Instala git, curl e nano (útil para edição dentro do container)
RUN apt-get update && apt-get install -y git curl nano && apt-get clean

# Define o diretório de trabalho
WORKDIR /app

# Clona o repositório e força atualização com git pull
RUN echo "Forçando cache buster: $CACHE_BUSTER" && \
    git clone https://github.com/madrijkaard/rkd-htf-learning.git . && \
    git pull

# Cria o arquivo .env diretamente no container
RUN echo "APP_NAME=rkd-htf-learning\nCAPTURE_INTERVAL_SECONDS=60\nSYMBOLS=[\"BTCUSDT\"]" > .env

# Cria a estrutura de diretórios necessários
RUN mkdir -p static && \
    mkdir -p data/asks && \
    mkdir -p data/bids

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo FastAPI
EXPOSE 8000

# Comando de inicialização do servidor + chamada ao endpoint
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
           sleep 20 && \
           curl -X POST http://localhost:8000/order-books/capture/start && \
           tail -f /dev/null"
