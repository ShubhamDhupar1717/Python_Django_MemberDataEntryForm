# Generated by Django 5.0.1 on 2024-01-08 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MemberData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fullname', models.CharField(max_length=100)),
                ('Email', models.CharField(max_length=250)),
                ('Dob', models.DateTimeField()),
                ('Resphone', models.CharField(max_length=20)),
                ('Altermobileno', models.CharField(max_length=20)),
                ('Resaddress', models.CharField(max_length=300)),
                ('Officeno', models.CharField(max_length=255)),
                ('Country', models.CharField(max_length=125)),
                ('Profilepic', models.ImageField(upload_to='pics')),
                ('Signature', models.ImageField(upload_to='pics')),
                ('Creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MemberBusinessData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Businessname', models.CharField(max_length=100)),
                ('Businessdetails', models.TextField()),
                ('Businessaddress', models.CharField(max_length=100)),
                ('Businesscity', models.CharField(max_length=20)),
                ('Businessemail', models.CharField(max_length=300)),
                ('Businesspostalcode', models.CharField(max_length=100)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PPMemberClub.memberdata')),
            ],
        ),
        migrations.CreateModel(
            name='MemberAddressData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Address', models.CharField(max_length=300)),
                ('Country', models.CharField(max_length=20)),
                ('State', models.CharField(max_length=100)),
                ('City', models.CharField(max_length=50)),
                ('Postalcode', models.CharField(max_length=10)),
                ('Addresstype', models.CharField(max_length=50)),
                ('Additionalinfo', models.TextField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PPMemberClub.memberdata')),
            ],
        ),
        migrations.CreateModel(
            name='MemberFamilyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('relation', models.CharField(max_length=100)),
                ('contactno', models.CharField(max_length=20)),
                ('homeaddress', models.CharField(max_length=300)),
                ('Spousename', models.CharField(max_length=200)),
                ('Spousedob', models.DateTimeField()),
                ('Childname', models.CharField(max_length=100)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PPMemberClub.memberdata')),
            ],
        ),
    ]
