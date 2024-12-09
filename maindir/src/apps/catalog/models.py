from django.db import models

class Product(models.Model):
    brand = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    build = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    type_suspension = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    popularity = models.IntegerField(default=0)

    def __str__(self):
        return self.name