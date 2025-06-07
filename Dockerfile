# Imagem base com Python 3.11
FROM python:3.11-slim

# Instala dependências do sistema necessárias para git e curl
RUN apt-get update && apt-get install -y git curl && apt-get clean

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Clona o repositório do projeto diretamente do GitHub
RUN git clone https://github.com/madrijkaard/rkd-htf-learning.git .

# Garante que a pasta 'static/' exista (necessária para o FastAPI mount)
RUN mkdir -p static

# Copia o arquivo .env do host para o container (deve estar no mesmo diretório do Dockerfile)
COPY .env .env

# Instala as dependências Python do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pela aplicação FastAPI
EXPOSE 8000

# Comando para iniciar o app, aguardar e iniciar captura automática
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
           sleep 20 && \
           curl -X POST http://localhost:8000/order-book/capture/start && \
           tail -f /dev/null"
