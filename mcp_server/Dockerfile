FROM python:3.11-slim
WORKDIR /app
COPY mcp_server/requirements.txt /app/mcp_server/requirements.txt
RUN pip install --no-cache-dir -r /app/mcp_server/requirements.txt
COPY mcp_server /app/mcp_server
ENV PYTHONPATH=/app
CMD ["python", "-m", "mcp_server.server"]
