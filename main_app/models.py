from django.db import models

# Create your models here.
class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()

    # Changing this instance method does not impact the database,
    # therefore no migration is needed
    def __str__(self):
        return f'{self.name} ({self.id})'
