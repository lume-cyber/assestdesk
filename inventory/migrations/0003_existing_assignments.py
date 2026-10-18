from django.db import migrations

def seed(apps, schema_editor):
    Asset = apps.get_model('inventory', 'Asset')
    Record = apps.get_model('inventory', 'AssignmentRecord')
    for asset in Asset.objects.exclude(assigned_to='').iterator():
        Record.objects.create(asset=asset, employee=asset.assigned_to, notes='Existing assignment at upgrade; original date unknown.')

class Migration(migrations.Migration):
    dependencies = [('inventory', '0002_asset_photo_data_assignmentrecord_servicerecord')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
