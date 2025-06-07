FROM python:3.11-slim

# Instala dependências básicas do sistema
RUN apt-get update && apt-get install -y git curl && apt-get clean

# Cria e entra no diretório de trabalho
WORKDIR /app

# Clona o repositório
RUN git clone https://github.com/madrijkaard/rkd-htf-learning.git .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do FastAPI
EXPOSE 8000

# Comando para iniciar uvicorn, esperar 10s e fazer POST
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
           sleep 10 && \
           curl -X POST http://localhost:8000/order-book/capture/start && \
           tail -f /dev/null"
