import argparse
import ConfigParser

from cornflake import fields, serializers
from cornflake.sqlalchemy_orm import ReferenceField
import tablib

from radar.app import Radar
from radar.database import db
from radar.exporter.exporters import exporter_map
from radar.models.groups import Group
from radar.models.users import User


def save(data, format, dest):
    with open(dest, 'wb') as f:
        data = data.export(format)
        f.write(data)


class GroupField(ReferenceField):
    model_class = Group


class UserField(ReferenceField):
    model_class = User


class ConfigSerializer(serializers.Serializer):
    anonymised = fields.BooleanField(required=False)
    data_group = GroupField(required=False)
    patient_group = GroupField(required=False)
    user = UserField(required=False)


def parse_config(config_parser):
    if config_parser.has_section('global'):
        data = dict(config_parser.items('global'))
    else:
        data = dict()

    serializer = ConfigSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    return validated_data


def create_exporters(config_parser):
    config = parse_config(config_parser)

    exporters = []

    for name in config_parser.sections():
        if name == 'global':
            continue

        exporter_class = exporter_map[name]

        data = dict(config_parser.items(name))
        exporter_config = exporter_class.parse_config(data)
        exporter_config = dict(
            config.items() +
            exporter_config.items()
        )
        exporter_config.update({'name': name})
        exporter = exporter_class(exporter_config)
        exporters.append((name, exporter))

    return exporters


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('config')
    argument_parser.add_argument('dest')
    args = argument_parser.parse_args()

    app = Radar()

    config_parser = ConfigParser.ConfigParser()
    config_parser.readfp(open(args.config))
    from radar.models import GroupPatient, Patient
    from sqlalchemy import and_
    with app.app_context():
        query = db.session.query(GroupPatient, Group, Patient).filter(
            and_(
                Group.code=='NURTURE',
                Patient.test==False,
                GroupPatient.group==Group,
                GroupPatient.patient==Patient
            )
        )

        exporters = create_exporters(config_parser)

        datasets = []

        # Export data
        for name, exporter in exporters:
            print 'Exporting {0}...'.format(name)
            exporter.run()
            # patient_list = []
            # for p in exporter._query:
            #     patient_list = [p for p in exporter._query]

            dataset = exporter.dataset

            dataset.title = name
            datasets.append(dataset)

        databook = tablib.Databook()

        for dataset in datasets:
            databook.add_sheet(dataset)

        save(databook, 'xlsx', args.dest)


if __name__ == '__main__':
    main()
