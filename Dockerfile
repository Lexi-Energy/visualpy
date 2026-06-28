FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml README.md ./
COPY visualpy/ visualpy/
COPY static/ static/
RUN pip install --no-cache-dir -e ".[llm]"

COPY tests/fixtures/agentic_workflows/ /demo_project/
RUN visualpy analyze /demo_project -o /demo_data.json

EXPOSE 8123
CMD ["visualpy", "serve", "--from-json", "/demo_data.json", "--host", "0.0.0.0", "--port", "8123"]