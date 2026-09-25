from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("utilisateurs", "0002_alter_utilisateur_managers")]

    operations = [
        migrations.AlterField(
            model_name="utilisateur",
            name="photo_profil",
            field=models.ImageField(default="profils/avatar-defaut.svg", upload_to="profils/"),
        ),
    ]
