from django.db import models

# Create your models here.

class Client(models.Model):
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    telegram_id = models.IntegerField()

    def __str__(self):
        return f"{self.full_name} ({self.contact_number})"
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"