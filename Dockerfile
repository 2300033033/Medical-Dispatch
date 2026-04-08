FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY environment.py .
COPY inference.py .
COPY app.py .
COPY openenv.yaml .
COPY README.md .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# Run the API server instead of inference.py
CMD ["python", "app.py"]
