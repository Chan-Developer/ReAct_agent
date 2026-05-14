FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    RESUME_COPILOT_HOST=0.0.0.0

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agents ./agents
COPY apps ./apps
COPY common ./common
COPY configs ./configs
COPY core ./core
COPY embeddings ./embeddings
COPY evaluation ./evaluation
COPY knowledge ./knowledge
COPY llm ./llm
COPY memory ./memory
COPY prompts ./prompts
COPY resume_copilot ./resume_copilot
COPY scripts ./scripts
COPY storage ./storage
COPY tools ./tools
COPY workflows ./workflows
COPY main.py ./

RUN pip install --upgrade pip && pip install .[docs]

EXPOSE 8000

CMD ["python", "-m", "resume_copilot.interfaces.http_server", "--host", "0.0.0.0", "--port", "8000"]
