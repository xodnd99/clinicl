FROM python:3.12

RUN apt-get update && apt-get install -y cmake
RUN pip install --upgrade pip

WORKDIR /app

COPY . /app



RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# CMD is now simplified; entrypoint.sh will handle the logic
CMD ["sh", "entrypoint.sh"]

