### Использование
Python test_task.py

Запускает сервис слушающий запросы на http://127.0.0.1:8080/

Использует web.py 
Формат запросов:
http://127.0.0.1:8080/?category=flight&category=show&category=games&category=onlycategory
- Конфигурационный файл считывается из корня проекта
- Изображения располагаются в папке static
- То есть формат пути в конфиге: image1.jpg;1;flight;airlplane (без ../static/)
