from functools import partial

import pyproj
from shapely.geometry import Point, mapping
from shapely.ops import transform


async def build_circle(point: Point, radius: int) -> dict:
    local_azimuthal_projection = (
        f"+proj=aeqd +R=6371000 +units=m +lat_0={point.y} +lon_0={point.x}"
    )
    wgs84_to_aeqd = partial(
        pyproj.transform,
        pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
        pyproj.Proj(local_azimuthal_projection),
    )
    aeqd_to_wgs84 = partial(
        pyproj.transform,
        pyproj.Proj(local_azimuthal_projection),
        pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
    )
    point_transformed = transform(wgs84_to_aeqd, point)
    buffer = point_transformed.buffer(radius)
    buffer_wgs84 = transform(aeqd_to_wgs84, buffer)
    return mapping(buffer_wgs84)
