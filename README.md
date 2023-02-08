# Allure Report Dwarf

Alure Report сервис с простейшим приемником пакетов с результатами тестов

## Зависимости

* python >= 3.10
* [Allure Report](https://docs.qameta.io/allure-report)

## Allure Report

Для настройки запуска allure report используются следующие переменные окружения:

```ini
ALLURE__ALLURE_PATH = /path/to/allure
ALLURE__REPORT__HOST = localhost
ALLURE__REPORT__PORT = 1154
ALLURE__RECEIVER__HOST = localhost
ALLURE__RECEIVER__PORT = 1133
```

* `ALLURE__ALLURE_PATH` - путь до исполняемого фала allure report (если не указано, то при запуске будет использоваться
  просто команда `allure`)
* `ALLURE__REPORT__HOST` - хост, на котором будет запущен allure report
* `ALLURE__REPORT__PORT` - порт, на котором будет запущен allure report
* `ALLURE__RECEIVER__HOST` - хост, на котором будет запущен приемник результатов
* `ALLURE__RECEIVER__PORT` - порт, на котором будет запущен приемник результатов

## Хранилище результатов

### Локальное хранилище

Если вы не хотите, чтобы данные сохранялись на ФХД, то укажите следующие переменные окружения:

```ini
STORAGE_TYPE = local
LOCAL_STORAGE_DIRPATH = /allure_backup
```

* `STORAGE_TYPE` - указывает на то, что в качестве ФХД будет использоваться локальная папка на ПК
* `LOCAL_STORAGE_DIRPATH` - путь к папке, в которой будут храниться результаты

Реализовано хранение пакетов с результатами выполнения тестов на внешнем файловом хранилище данных (далее ФХД)  
В данный момент пока есть поддержка [seafile](https://www.seafile.com) и [minio](https://min.io/).

### Seafile

Для интеграции с seafile просто укажете следующие переменные окружения:

```ini
STORAGE_TYPE = seafile
SEAFILE__URL = http://localhost
SEAFILE__USERNAME = my@example.com
SEAFILE__PASSWORD = Test123456
SEAFILE__REPO_ID = 600cfdca-8b07-4ac7-93ef-c1c40220ed8b
SEAFILE__DIRPATH = /allure_backups
```

* `STORAGE_TYPE` - указывает на то, что в качестве ФХД будет использоваться сервис seafile
* `SEAFILE__URL` - адрес сервиса seafile
* `SEAFILE__USERNAME` и `SEAFILE__PASSWORD` - данные для доступа к seafile
* `SEAFILE__REPO_ID` - репозиторий seafile, в котором будут сохраняться результаты
* `SEAFILE__DIRPATH` - путь к папке внутри репозитория, в которой будут храниться результаты

### MinIO

Для интеграции с minio просто укажете следующие переменные окружения:

```ini
STORAGE_TYPE = minio
MINIO__ENDPOINT = localhost:8080
MINIO__ACCESS_KEY = access_key
MINIO__SECRET_KEY = secret_key
MINIO__SECURE = true
MINIO__REGION = ru-central1
MINIO__BUCKET_NAME = bucket_name
MINIO__DIRPATH = allure_backups
```

* `STORAGE_TYPE` - указывает на то, что в качестве ФХД будет использоваться сервис minio
* `MINIO__ENDPOINT` - адрес сервиса minio (указывается без схемы http/https)
* `MINIO__ACCESS_KEY` и `MINIO__SECRET_KEY` - данные для доступа к minio
* `MINIO__SECURE` - признак использования TLS
* `MINIO__REGION` - регион авторизации minio
* `MINIO__BUCKET_NAME` - наименование бакета, где будут храниться результаты 
* `MINIO__DIRPATH` - путь к папке внутри бакета, в которой будут храниться результаты

## API для приема результатов

Данные принимаются zip архивом, в котором находятся результаты о прохождения тестов в формате Allure Report.

Запрос на передачу пакета с результатами:

```bash
curl --request POST \
  --url http://{{receiverUrl}}/upload_results \
  --header 'Content-Type: multipart/form-data' \
  --form file=@/path/to/package.zip
```

Эти результаты будут распакованы в папку и будет вызвана команда `allure generate` для генерации отчета на основе этих
результатов.
Также данные пакет будет сохранен на ФХД, чтобы была возможность восстановить отчеты при неожиданном сбое сервиса

В итоге вы сможете увидеть отчет в allure report

## Восстановление результатов при старте сервиса

При старте сервиса происходит скачивание всех пакетов с ФХД и генерация отчета
