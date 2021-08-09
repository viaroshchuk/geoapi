import json

import geojson
from sqlalchemy import create_engine
from sqlalchemy import insert

from app.db import fields

engine = create_engine(
    'postgresql://postgres:postgres@geoapi-postgres-service/postgres'
)
with open('data_dump') as file:
    lines = file.readlines()
    total = len(lines)
    i = 0
    with engine.connect() as conn:
        for line in lines:
            data = geojson.loads(line)
            conn.execute(insert(fields).values(
                id=data['properties']['id'],
                crop=data['properties']['crop'],
                productivity=data['properties']['productivity'],
                area=data['properties']['area_ha'],
                region=data['properties']['region'],
                geometry=json.dumps(data['geometry']),
            ))
            i += 1
            print(f'{i}/{total}')
