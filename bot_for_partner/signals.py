
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail 
from django.conf import settings
from asgiref.sync import async_to_sync

from telegram import Bot

from .models import ApartmentRequest
from .management.commands.keyboard.main import get_apartment_request_keyboard

@receiver(post_save, sender=ApartmentRequest)
def send_request_notification(sender, instance:ApartmentRequest, created, **kwargs):
    if created:
        print("asdasd")
        bot = Bot(token=settings.TELEGRAM_TOKEN)
        apartment = instance.apartment
        seller_telegram_id = apartment.owner.telegram_id 

        message = (
            f"У вас новый запрос на квартиру:\n"
            f"Квартира: {apartment.address}\n"
            f"Заявка от: {instance.full_name}\n"
            f"Телефон: {instance.phone_number}\n"
            f"Пользователь: {instance.user_username}\n"
            f"Дата заявки: {instance.request_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        keyboard = get_apartment_request_keyboard(instance.id)
        async_to_sync(bot.send_message)(
            chat_id=seller_telegram_id,
            text=message,
            reply_markup=keyboard
        )
        return
    else:
        
        if instance.status == "REJECTED":
            bot = Bot(token=settings.CLIENT_TELEGRAM_TOKEN)
            apartment = instance.apartment
            seller_telegram_id = apartment.owner.telegram_id 

            
            message = (
                f"Ваш запрос на квартиру был отклонен:\n"
                f"Квартира: {apartment.address}\n"
                f"Владелец: {apartment.owner.name}\n"
                f"Дата заявки: {instance.request_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            async_to_sync(bot.send_message)(
            chat_id=seller_telegram_id,
            text=message,
            )
            instance.delete()
            return
        
        elif instance.status == "ACCEPTED":
            bot = Bot(token=settings.CLIENT_TELEGRAM_TOKEN)
            apartment = instance.apartment
            seller_telegram_id = apartment.owner.telegram_id 

            message = (
                f"Ваш запрос на квартиру был Принят:\n"
                f"Квартира: {apartment.address}\n"
                f"Владелец: {apartment.owner.name}\n"
                f"Телефон Владелеца: {apartment.owner.contact_number}\n"
                f"Дата заявки: {instance.request_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            async_to_sync(bot.send_message)(
            chat_id=seller_telegram_id,
            text=message,
            )
            return 
