import json

import geojson
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import RouteTableDef
from aiohttp.web import json_response
from jsonschema import ValidationError
from jsonschema import validate
from shapely.geometry import Point
from sqlalchemy.sql import func
from sqlalchemy.sql import select

from app.api.schemas import EQUIDISTANT_FIELDS_SCHEMA
from app.api.schemas import STATS_BY_REGION_SCHEMA
from app.api.utils import build_circle
from app.db import fields

routes = RouteTableDef()
MAX_GEOMS = 10000


@routes.post('/v1/equidistant_fields')
async def equidistant_fields(request: Request) -> Response:
    try:
        data = await request.json()
        validate(data, EQUIDISTANT_FIELDS_SCHEMA)
        geom = geojson.Point(
            coordinates=data.get('geometry').get('coordinates'),
        )
        if not geom.is_valid:
            raise ValidationError(message='Invalid GeoJson')
    except ValidationError as error:
        return json_response(data=error.message, status=400)
    except json.JSONDecodeError:
        return json_response(data='Bad JSON', status=400)

    query = select(
        fields.c.crop,
        fields.c.productivity,
        fields.c.region,
        fields.c.area,
        func.ST_AsGeoJson(fields.c.geometry).label('geometry'),
    ).where(
        func.ST_Overlaps(
            func.ST_GeomFromGeoJson(
                json.dumps(await build_circle(
                    Point(*data['geometry']['coordinates']),
                    data.get('distance'),
                ))
            ),
            fields.c.geometry,
        )
    ).limit(MAX_GEOMS)
    if data.get('crop'):
        query = query.where(fields.c.crop == data['crop'])

    async with request.app['db_engine'].connect() as conn:
        rows = (await conn.execute(query)).fetchall()

    return json_response(
        geojson.FeatureCollection([
            geojson.Feature(
                properties={
                    'crop': row.crop,
                    'productivity_estimation': row.productivity,
                    'region_code': row.region,
                    'area_ha': row.area,
                },
                geometry=geojson.loads(row.geometry)
            ) for row in rows
        ])
    )


@routes.post('/v1/fields_inside_parallelogram')
async def fields_inside_parallelogram(request: Request) -> Response:
    try:
        data = await request.json()
        geom = geojson.Polygon(
            coordinates=data.get('geometry').get('coordinates'),
        )
        if not geom.is_valid:
            raise ValidationError(message='Invalid GeoJson')
        elif len(geom.coordinates[0]) != 5:
            raise ValidationError(message='Invalid polygon')
        # TODO: check if points form parallelogram
    except ValidationError as error:
        return json_response(data=error.message, status=400)
    except json.JSONDecodeError:
        return json_response(data='Bad JSON', status=400)

    query = select(
        fields.c.crop,
        fields.c.productivity,
        fields.c.region,
        fields.c.area,
        func.ST_AsGeoJson(fields.c.geometry).label('geometry'),
    ).where(
        func.ST_ContainsProperly(
            func.ST_GeomFromGeoJson(geojson.dumps(geom)),
            fields.c.geometry,
        )
    ).limit(MAX_GEOMS)
    if data.get('crop'):
        query = query.where(fields.c.crop == data['crop'])

    async with request.app['db_engine'].connect() as conn:
        rows = (await conn.execute(query)).fetchall()

    return json_response(
        geojson.FeatureCollection([
            geojson.Feature(
                properties={
                    'crop': row.crop,
                    'productivity_estimation': row.productivity,
                    'region_code': row.region,
                    'area_ha': row.area,
                },
                geometry=geojson.loads(row.geometry)
            ) for row in rows
        ])
    )


@routes.post('/v1/fields_intersecting_with_geometry')
async def fields_intersecting_with_geometry(request: Request) -> Response:
    try:
        data = await request.json()
        geom = geojson.loads(json.dumps(data.get('geometry')))
        if not geom.is_valid:
            raise ValidationError(message='Invalid GeoJson')
        elif not isinstance(geom, geojson.geometry.Geometry):
            raise ValidationError(message='Not geometry')
    except ValidationError as error:
        return json_response(data=error.message, status=400)
    except json.JSONDecodeError:
        return json_response(data='Bad JSON', status=400)

    query = select(
        fields.c.crop,
        fields.c.productivity,
        fields.c.region,
        fields.c.area,
        func.ST_AsGeoJson(fields.c.geometry).label('geometry'),
    ).where(
        func.ST_Intersects(
            func.ST_GeomFromGeoJson(geojson.dumps(geom)),
            fields.c.geometry,
        )
    ).limit(MAX_GEOMS)
    if data.get('crop'):
        query = query.where(fields.c.crop == data['crop'])

    async with request.app['db_engine'].connect() as conn:
        rows = (await conn.execute(query)).fetchall()

    return json_response(
        geojson.FeatureCollection([
            geojson.Feature(
                properties={
                    'crop': row.crop,
                    'productivity_estimation': row.productivity,
                    'region_code': row.region,
                    'area_ha': row.area,
                },
                geometry=geojson.loads(row.geometry)
            ) for row in rows
        ])
    )


@routes.post('/v1/stats_by_region')
async def stats_by_region(request: Request) -> Response:
    try:
        data = await request.json()
        validate(data, STATS_BY_REGION_SCHEMA)
    except ValidationError as error:
        return json_response(data=error.message, status=400)
    except json.JSONDecodeError:
        return json_response(data='Bad JSON', status=400)

    async with request.app['db_engine'].connect() as conn:
        rows = (await conn.execute(
            select(
                fields.c.crop,
                func.sum(fields.c.area).label('total_area'),
                func.sum(fields.c.productivity).label('total_yield'),
            ).where(
                fields.c.region == data['region'],
                fields.c.crop != None,  # noqa
            ).group_by(
                fields.c.crop
            )
        )).fetchall()

    return json_response(
        {
            row.crop: {
                'total_area': row.total_area,
                'total_yield': row.total_yield,
                'average_yield': row.total_yield/row.total_area,
            } for row in rows
        }
    )
