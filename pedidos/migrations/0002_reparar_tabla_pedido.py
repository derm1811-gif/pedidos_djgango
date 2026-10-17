from django.db import migrations


def reparar_tabla_pedido(apps, schema_editor):
    pedido = apps.get_model('pedidos', 'Pedido')
    conexion = schema_editor.connection
    tabla = pedido._meta.db_table
    respaldo = f'{tabla}_legacy'
    tablas = set(conexion.introspection.table_names())

    if tabla not in tablas:
        schema_editor.create_model(pedido)
        return

    with conexion.cursor() as cursor:
        columnas = {
            columna.name
            for columna in conexion.introspection.get_table_description(cursor, tabla)
        }

    if 'numero_pedido' in columnas:
        return

    if respaldo in tablas:
        raise RuntimeError(
            f'No se puede respaldar {tabla}: ya existe la tabla {respaldo}.'
        )

    tabla_citada = conexion.ops.quote_name(tabla)
    respaldo_citado = conexion.ops.quote_name(respaldo)
    schema_editor.execute(f'ALTER TABLE {tabla_citada} RENAME TO {respaldo_citado}')
    schema_editor.create_model(pedido)


def revertir_reparacion(apps, schema_editor):
    pedido = apps.get_model('pedidos', 'Pedido')
    conexion = schema_editor.connection
    tabla = pedido._meta.db_table
    respaldo = f'{tabla}_legacy'
    tablas = set(conexion.introspection.table_names())

    if tabla in tablas:
        schema_editor.delete_model(pedido)
    if respaldo in tablas:
        schema_editor.execute(
            f'ALTER TABLE {conexion.ops.quote_name(respaldo)} '
            f'RENAME TO {conexion.ops.quote_name(tabla)}'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reparar_tabla_pedido, revertir_reparacion),
    ]