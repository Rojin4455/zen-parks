# Generated by Django 5.1.7 on 2025-03-25 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_contact'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opportunity',
            old_name='location_id',
            new_name='assigned',
        ),
        migrations.RenameField(
            model_name='opportunity',
            old_name='location_name',
            new_name='lost_reason_id',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='opportunity',
            name='days_since_last_stage_change',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='days_since_last_status_change',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='days_since_last_updated',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='engagement_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='followers',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='lost_reason_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='pipeline_stage_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='updated_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
