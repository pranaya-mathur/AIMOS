
FROM python:3.10
WORKDIR /app
ENV PROMPTS_DIR=/app/prompts
COPY prompts /app/prompts
COPY backend /app
COPY scripts /app/scripts
RUN pip install -r requirements.txt
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
