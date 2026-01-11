from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_chapter_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='book_pdfs/', verbose_name='PDF文件'),
        ),
    ]


