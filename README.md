# GEOAPI
Прежде всего поместите файл с записями в корень проекта, назвав его ``data_dump``
## Локальный запуск
Запуск контейнеров
```commandline
docker-compose up
```
Создание таблицы и заполнение базы
```commandline
docker exec -it *geoapi_geoapi-app container id* python scripts/init_db.py
docker exec -it *geoapi_geoapi-app container id* python scripts/fill_db.py
```

## Развертывание в k8s
Создайте объекты кубернетеса в кластере
```commandline
kubectl apply -f k8s/postgres.yaml 
kubectl apply -f k8s/app.yaml 
```
Дождитесь запуска пода приложения
```commandline
kubectl get pods -l app=geoapi-app
NAME                                    READY   STATUS    RESTARTS   AGE
geoapi-app-deployment-9c5787db8-kxs88   1/1     Running   1          42h
```
Сетап базы аналогичный с локальным
```commandline
kubectl exec -it geoapi-app-deployment-9c5787db8-kxs88 python scripts/init_db.py
kubectl exec -it geoapi-app-deployment-9c5787db8-kxs88 python scripts/fill_db.py
```

## API
В сервисе предусмотрено 4 эндпоинта:
- http://0.0.0.0:8080/v1/equidistant_fields
- http://0.0.0.0:8080/v1/fields_inside_parallelogram
- http://0.0.0.0:8080/v1/fields_intersecting_with_geometry
- http://0.0.0.0:8080/v1/stats_by_region

В случае невалидного тела эндпоинты возвращают 400 с сообщением об ошибке прямо в теле ответа.
Пример:
```json
"Bad JSON"
```

### v1/equidistant_fields
Получение набора полей равноудаленных от определенной точки.
#### Тело запроса
```json
{
	"geometry": {  // Геометрия в формате geojson
		"type": "Point",
		"coordinates": [
			<float> // e.g. 4.6636962890625
			<float> // e.g. 47.97889140226657
		]
	},
	"distance": <int>, // Дистанция в метрах
	"crop": <str, not mandatory> // Название куоьтуры
}
```
#### Ответ
GeoJSON FeatureCollection с properties:
- crop - string, nullable
- productivity_estimation - float, nullable
- region_code - sting, nullable
- area_ha - float

### v1/fields_inside_parallelogram
Получение набора полей внутри параллелограмма с заданными вершинами.
#### Тело запроса
```json
{
  "geometry": {  // Полигон, которым представлен параллелограмм
    "type": "Polygon",
    "coordinates": [...]
  },
  "crop": <str, not mandatory>
}
```
#### Ответ
GeoJSON FeatureCollection с properties:
- crop - string, nullable
- productivity_estimation - float, nullable
- region_code - sting, nullable
- area_ha - float

### v1/fields_intersecting_with_geometry
Получение набора полей, что пересекаются с запрашиваемой геометрией.
#### Тело запроса
```json
{
  "geometry": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "crop": <str, not mandatory>
}
```
#### Ответ
GeoJSON FeatureCollection с properties:
- crop - string, nullable
- productivity_estimation - float, nullable
- region_code - sting, nullable
- area_ha - float

### v1/stats_by_region
Получение информации по культурах в даном регионе.
#### Тело запроса
```json
{
  "region": <str> // Регион
}
```
#### Ответ
```json
{
  <crop name, str>: {
    "total_area": <float>,
    "total_yield": <float, nullable>,
    "average_yield": <float, nullable>
  },
  {
    ... // Структура такого же вида
  },
  ...
}
```