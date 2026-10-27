# Reflex + SQLite en un solo contenedor:  docker build -t agrotech . && docker run -p 3000:3000 -p 8000:8000 -v agrotech-datos:/app/datos agrotech
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --no-cache-dir "reflex[db]>=0.10.0" "fastapi>=0.115" "requests>=2.31" "fpdf2>=2.7"
COPY . .
ENV AGROTECH_DB_URL=sqlite:////app/datos/agrotech.db
EXPOSE 3000 8000
CMD ["sh", "-c", "python -m agrotechEFA2026.db.seed; reflex run --env prod"]
