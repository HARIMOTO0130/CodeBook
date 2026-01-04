# Generated manually to add video_url to Chapter
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='video_url',
            field=models.URLField(blank=True, null=True, verbose_name='视频URL'),
        ),
    ]


