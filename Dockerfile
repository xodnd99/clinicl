FROM python:3.12

RUN apt-get update && apt-get install -y cmake
RUN pip install --upgrade pip

WORKDIR /app

COPY . /app

# Download wait-for-it.sh
RUN curl -o /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /wait-for-it.sh


RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "./entrypoint.sh"]


