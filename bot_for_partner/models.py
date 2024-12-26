from django.db import models


# Create your models here.


class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя владельца")
    contact_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Контактный номер")
    email = models.EmailField(blank=True, null=True, verbose_name="Электронная почта")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Владелец квартиры"
        verbose_name_plural = "Владельцы квартир"


class City(models.Model):
    name = models.CharField(max_length=255, verbose_name="Город")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class District(models.Model):
    name = models.CharField(max_length=255, verbose_name="Район")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts', verbose_name="Город")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"


class Neighborhood(models.Model):
    name = models.CharField(max_length=255, verbose_name="Микрорайон")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='neighborhoods', verbose_name="Район")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Микрорайон"
        verbose_name_plural = "Микрорайоны"


class Apartment(models.Model):
    number_of_rooms = models.PositiveIntegerField(verbose_name="Количество комнат")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='apartments',
                             verbose_name="Город")
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='apartments',
                                 verbose_name="Район")
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='apartments', verbose_name="Микрорайон")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес квартиры")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='apartments', verbose_name="Владелец")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    def __str__(self):
        return f'Квартира в {self.city.name if self.city else "неизвестный город"}, {self.address}'

    class Meta:
        verbose_name = "Квартира"
        verbose_name_plural = "Квартиры"


class Photo(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='photos', verbose_name="Квартира")
    image = models.ImageField(upload_to='photos/', verbose_name="Фотография")
    photo_id = models.CharField(max_length=500, blank=True,null=True)

    def __str__(self):
        return f'Фотография {self.id} для квартиры {self.apartment.id}'

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"


class ApartmentRequest(models.Model):
    STATUS_CHOICES = (
        ('IN_PROCESSING', 'IN_PROCESSING'),
        ('REJECTED', 'REJECTED'),
        ('ACCEPTED', 'ACCEPTED'),
    )
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='requests', verbose_name="Квартира")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    status = models.CharField(max_length=255, verbose_name="Статус заявки",choices=STATUS_CHOICES,default='IN_PROCESSING')
    user_telegram_id = models.CharField(max_length=255, verbose_name="Пользователь")
    phone_number = models.CharField(max_length=255, verbose_name="Телефон")
    user_username = models.CharField(max_length=255,verbose_name="Имя Пользователя")
    full_name = models.CharField(max_length=255,verbose_name="ФИО")

    class Meta:
        verbose_name = "Заявка на квартиру"
        verbose_name_plural = "Заявки на квартиры"

    def __str__(self) -> str:
        return f"{self.apartment}-{self.phone_number}"   