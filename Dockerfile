# Окружение находится в Dockerfile.env
FROM allure-env

EXPOSE 1154
EXPOSE 1133

WORKDIR /app
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY . .

CMD python main.py