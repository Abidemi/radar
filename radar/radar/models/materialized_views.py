from sqlalchemy import Table, Column, event, MetaData
from sqlalchemy.schema import DDLElement
from sqlalchemy.ext import compiler

from radar.database import db


class CreateMaterializedView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


class DropMaterializedView(DDLElement):
    def __init__(self, name):
        self.name = name


@compiler.compiles(CreateMaterializedView)
def compile_create_materialized_view(element, compiler, **kwargs):
    return 'CREATE MATERIALIZED VIEW {name} AS {query}'.format(
        name=element.name,
        query=compiler.sql_compiler.process(element.selectable, literal_binds=True)
    )


@compiler.compiles(DropMaterializedView)
def compile_drop_materialized_view(element, compiler, **kwargs):
    return 'DROP MATERIALIZED VIEW IF EXISTS {name}'.format(name=element.name)


def create_materialized_view(name, selectable, *args):
    # Add the table to a new MetaData object so CREATE TABLE isn't run
    tmp_metadata = MetaData()
    table_args = [Column(c.name, c.type) for c in selectable.c]
    table_args.extend(args)
    t = Table(name, tmp_metadata, *table_args)

    metadata = db.Model.metadata
    event.listen(metadata, 'after_create', CreateMaterializedView(name, selectable))
    event.listen(metadata, 'before_drop', DropMaterializedView(name))

    return t
