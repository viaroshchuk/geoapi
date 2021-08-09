from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://postgres:postgres@geoapi-postgres-service/postgres'
)

with engine.connect() as conn:
    conn.execute(
        '''
            create table if not exists fields (
            id integer primary key,
            crop varchar(20),
            productivity float,
            area float not null,
            region varchar(20),
            geometry geometry(GEOMETRY) not null
        );
        
        create index if not exists fields_geom_idx on fields using GIST(geometry);
        create index if not exists fields_crop_idx on fields (crop);
        create index if not exists fields_region_idx on fields (region);
    '''
    )
print('Created tables and indexes')
