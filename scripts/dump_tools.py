from datetime import datetime, date

import unicodecsv as csv


def to_str(value):
    if isinstance(value, datetime):
        value = datetime_to_str(value)
    elif isinstance(value, date):
        value = date_to_str(value)
    elif isinstance(value, dict):
        value = dict_to_str(value)
    elif isinstance(value, list):
        value = list_to_str(value)
    elif value in ['\0', '\1']:
        # Bit type
        value = int(value == '\1')

    return value


def list_to_str(value):
    return ', '.join(value)


def dict_to_str(value):
    return ', '.join(['%s=%s' % (k, v) for k, v in value.items()])


def date_to_str(value):
    return '%04d-%02d-%02d' % (
        value.year,
        value.month,
        value.day,
    )


def datetime_to_str(value):
    return '%04d-%02d-%02d %02d:%02d:%02d' % (
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second,
    )


def rows_to_csv(rows, output_file):
    writer = csv.writer(output_file, encoding='utf-8')

    first = True

    for row in rows:
        if first:
            writer.writerow(row.keys())
            first = False

        writer.writerow([to_str(x) for x in row.values()])
