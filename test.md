запустите сервер:
python app.py

должны увидеть:

text
Запуск сервера на http://0.0.0.0:8000
Доступный эндпоинт: POST /api/v1/robinson_cruise
Нажмите CTRL+C для остановки сервера
--------------------------------------------------
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

Теперь протестируем работу API
Тест 1: Простой маршрут (должен долететь)
bash
curl -X POST http://localhost:8000/api/v1/robinson_cruise \
  -H "Content-Type: application/json" \
  -d "{\"mass_shuttle\": 1000.0, \"mass_fuel_unit\": 1.0, \"power_per_unit\": 1000.0, \"oxygen_time\": 864000, \"total_fuel\": 10000, \"fuel_consumption\": 3.0, \"bodies\": [], \"edges\": [{\"from\": \"start_point\", \"to\": \"rescue_point\", \"distance\": 100000000}]}"

Тест 2: С гравитационным манёвром
bash
curl -X POST http://localhost:8000/api/v1/robinson_cruise \
  -H "Content-Type: application/json" \
  -d "{\"mass_shuttle\": 1000.0, \"mass_fuel_unit\": 1.0, \"power_per_unit\": 1000.0, \"oxygen_time\": 864000, \"total_fuel\": 7000, \"fuel_consumption\": 3.0, \"bodies\": [{\"id\": \"planet1\", \"gravity_assists\": [{\"velocity_gain\": 10000.0, \"fuel_consumption\": 40, \"time_to_execute\": 1095}]}], \"edges\": [{\"from\": \"start_point\", \"to\": \"planet1\", \"distance\": 200000000}, {\"from\": \"planet1\", \"to\": \"rescue_point\", \"distance\": 4000000}]}"

Тест 3: Некорректные данные (должен вернуть ошибку)
bash
curl -X POST http://localhost:8000/api/v1/robinson_cruise \
  -H "Content-Type: application/json" \
  -d "{\"mass_shuttle\": -1000}"

остановить сервер:
Ctrl + C

Хотя API работает через POST-запросы (не GET), вы можете использовать браузер для отправки тестовых запросов. Вот несколько способов:
FastAPI автоматически создает интерактивную документацию. Откройте в браузере:
http://localhost:8000/docs

Вы увидите красивый интерфейс Swagger UI, где можно:
Нажать на эндпоинт POST /api/v1/robinson_cruise
Нажать кнопку "Try it out"
Вставить JSON-данные
Нажать "Execute" и увидеть результат

Пример 1: Прямой полет (успешный)
{
  "mass_shuttle": 1000.0,
  "mass_fuel_unit": 1.0,
  "power_per_unit": 1000.0,
  "oxygen_time": 864000,
  "total_fuel": 10000,
  "fuel_consumption": 3.0,
  "bodies": [],
  "edges": [
    {
      "from": "start_point",
      "to": "rescue_point",
      "distance": 100000000
    }
  ]
}

Пример 2: С гравитационным маневром через планету
json
{
  "mass_shuttle": 1000.0,
  "mass_fuel_unit": 1.0,
  "power_per_unit": 1000.0,
  "oxygen_time": 864000,
  "total_fuel": 7000,
  "fuel_consumption": 3.0,
  "bodies": [
    {
      "id": "planet1",
      "gravity_assists": [
        {
          "velocity_gain": 10000.0,
          "fuel_consumption": 40,
          "time_to_execute": 1095
        }
      ]
    }
  ],
  "edges": [
    {
      "from": "start_point",
      "to": "planet1",
      "distance": 200000000
    },
    {
      "from": "planet1",
      "to": "rescue_point",
      "distance": 4000000
    }
  ]
}
Пример 3: Два гравитационных маневра
json
{
  "mass_shuttle": 1000.0,
  "mass_fuel_unit": 1.0,
  "power_per_unit": 1000.0,
  "oxygen_time": 864000,
  "total_fuel": 8000,
  "fuel_consumption": 3.0,
  "bodies": [
    {
      "id": "planet1",
      "gravity_assists": [
        {
          "velocity_gain": 10000.0,
          "fuel_consumption": 40,
          "time_to_execute": 1095
        },
        {
          "velocity_gain": 24000.0,
          "fuel_consumption": 84,
          "time_to_execute": 2026
        }
      ]
    },
    {
      "id": "gas_giant",
      "gravity_assists": [
        {
          "velocity_gain": 50000.0,
          "fuel_consumption": 150,
          "time_to_execute": 3600
        }
      ]
    }
  ],
  "edges": [
    {
      "from": "start_point",
      "to": "planet1",
      "distance": 200000000
    },
    {
      "from": "planet1",
      "to": "gas_giant",
      "distance": 500000000
    },
    {
      "from": "gas_giant",
      "to": "rescue_point",
      "distance": 300000000
    }
  ]
}
Пример 4: Невозможный полет (мало топлива)
json
{
  "mass_shuttle": 1000.0,
  "mass_fuel_unit": 1.0,
  "power_per_unit": 1000.0,
  "oxygen_time": 864000,
  "total_fuel": 100,
  "fuel_consumption": 3.0,
  "bodies": [],
  "edges": [
    {
      "from": "start_point",
      "to": "rescue_point",
      "distance": 100000000
    }
  ]
}
Пример 5: Некорректные данные (должен вернуть ошибку)
json
{
  "mass_shuttle": -1000.0,
  "mass_fuel_unit": 1.0,
  "power_per_unit": 1000.0,
  "oxygen_time": 864000,
  "total_fuel": 10000,
  "fuel_consumption": 3.0,
  "bodies": [],
  "edges": []
}


