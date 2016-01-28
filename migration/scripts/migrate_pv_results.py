from sqlalchemy import text, create_engine
import click

from radar_migration import Migration, EXCLUDED_UNITS, tables, ObservationNotFound, GroupNotFound
from radar_migration.utils import grouper

PV_CODE_MAP = {
    'ADJUSTEDCA': 'ADJUSTEDCALCIUM',
    'CHOLESTERO': 'CHOLESTEROL',
    'TRANSFERRI': 'TRANSFERRIN',
    'ALKALINE PHOSPHATASE': 'ALP',
    'FERR': 'FERRITIN',
    'HBA1C (IFCC)': 'HBA1C',
    'RANDOM PLASMA GLUCOSE': 'GLUCOSE',
    'RANDOM PLASMA GLUCOSE:': 'GLUCOSE',
}


def convert_pv_code(value):
    value = value.upper()
    value = PV_CODE_MAP.get(value, value)
    return value


def migrate_pv_results(old_conn, new_conn):
    m = Migration(new_conn)

    rows = old_conn.execute(text("""
        SELECT
            patient.radarNo,
            testresult.unitcode,
            testcode,
            datestamp,
            value
        FROM testresult
        JOIN patient ON testresult.nhsno = patient.nhsno
        JOIN unit ON testresult.unitcode = unit.unitcode
        WHERE
            patient.radarNo is not NULL AND
            patient.unitcode NOT IN {0} AND
            unit.sourceType = 'renalunit' AND
            unit.unitcode NOT IN {0} AND
            testcode NOT REGEXP '^[0-9]+$' and
            testcode NOT IN (
                '4258.', '426..', '428..', '429..', '42A..',
                '42J..', '42K..', '42L..', '42M..', '42N..',
                '42Z5.', '42Z7', '44EC.', '44F..', '44G3.',
                '44I9.', '44IC.', '44M3.', '44M5.', '451E.',
                '46I..', '42Z7.', '46N3.'
            )
    """.format(EXCLUDED_UNITS)))

    for i, rows in enumerate(grouper(100000, rows), start=1):
        print 'batch', i

        batch = []

        for row in rows:
            pv_code = convert_pv_code(row['testcode'])

            try:
                observation_id = m.get_observation_id(pv_code=pv_code)
            except ObservationNotFound:
                print pv_code, 'not found'

            try:
                value = float(row['value'])
            except ValueError:
                continue

            value = str(value)

            group_code = row['unitcode']
            source_group_id = None
            source_type = None

            try:
                source_group_id = m.get_hospital_id(group_code)
                source_type = m.ukrdc_source_type
            except GroupNotFound:
                pass

            # Otherwise check the data was entered by a cohort
            if source_group_id is None:
                try:
                    m.get_cohort_id(group_code)
                except GroupNotFound:
                    print 'group', group_code, 'not found'
                    continue

                source_group_id = m.group_id
                source_type = m.radar_source_type

            batch.append(dict(
                patient_id=row['radarNo'],
                source_group_id=source_group_id,
                source_type=source_type,
                observation_id=observation_id,
                date=row['datestamp'],
                value=value,
                created_user_id=m.user_id,
                modified_user_id=m.user_id,
            ))

        new_conn.execute(tables.results.insert(), batch)


@click.command()
@click.argument('src')
@click.argument('dest')
def cli(src, dest):
    src_engine = create_engine(src)
    dest_engine = create_engine(dest)

    src_conn = src_engine.connect()
    dest_conn = dest_engine.connect()

    with dest_conn.begin():
        migrate_pv_results(src_conn, dest_conn)


if __name__ == '__main__':
    cli()
