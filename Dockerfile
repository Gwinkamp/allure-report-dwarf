# Окружение находится в Dockerfile.env
FROM gwinkamp/allure-report-dwarf-env:latest

EXPOSE 1154
EXPOSE 1133

WORKDIR /app
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY . .

CMD python main.py