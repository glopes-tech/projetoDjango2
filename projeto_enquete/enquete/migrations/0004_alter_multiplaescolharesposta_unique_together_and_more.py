# Generated by Django 5.2.1 on 2025-05-20 16:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enquete', '0003_aluno_user_alter_aluno_nome'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='multiplaescolharesposta',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='resposta',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='multiplaescolharesposta',
            name='aluno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='enquete.aluno'),
        ),
        migrations.AlterField(
            model_name='resposta',
            name='aluno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='enquete.aluno'),
        ),
    ]
