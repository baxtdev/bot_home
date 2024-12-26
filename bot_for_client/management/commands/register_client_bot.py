from django.conf import settings
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from telegram import Update, ReplyKeyboardMarkup,CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton,InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)

from root.utils import acreate_build_url
from bot_for_partner.models import Owner,City,ApartmentRequest,District,Apartment,Neighborhood,Photo
from .apartament import *
from .text.main import apartament_info
from .keyboard.main import filter_menu_keyboard,city_filter_keyboard,district_filter_keyboard,\
    neighborhood_filter_keyboard,apartment_request_buttons,navigation_buttons,\
    rooms_filter_keyboard,generate_pagination_buttons
from .profile import *
from .logger import logger

APARTMENTS_PER_PAGE = 6

class Command(BaseCommand):
    help = 'Run the Telegram bot for clients'

    def handle(self, *args, **kwargs):
        application = Application.builder().token(settings.CLIENT_TELEGRAM_TOKEN).build()

        async def main(update: Update, context: CallbackContext):
            """Команда /start для клиента"""
            await update.message.reply_text(
                "Добро пожаловать! Выберите, по какому критерию хотите отфильтровать квартиры:",
                reply_markup=filter_menu_keyboard()
            )

        async def handle_filter_choice(update: Update, context: CallbackContext):
            """Обработка выбора фильтрации"""
            query = update.callback_query
            await query.answer()

            data = query.data

            if data == "filter_city":
                await query.edit_message_text("Выберите город:", reply_markup=await city_filter_keyboard())
            
            elif data.startswith("city_"):
                city_id = data.split("_")[1]
                context.user_data["city_id"] = city_id
                await query.edit_message_text("Выберите район:", reply_markup=district_filter_keyboard(city_id))

        async def view_apartment_details(update: Update, context: CallbackContext):
            """Просмотр деталей квартиры и возможность отправить запрос на аренду"""
            query = update.callback_query
            await query.answer()

            apartment_id = int(query.data.split("_")[1])
            apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)

            message = (
                f"Квартира в городе: {apartment.city.name}\n"
                f"Адрес: {apartment.address}\n"
                f"Комнат: {apartment.rooms}\n"
                f"Цена: {apartment.price}\n"
                "Хотите арендовать?"
            )

            await query.edit_message_text(
                text=message, 
                reply_markup=apartment_request_buttons(apartment_id)
            )

        async def send_rent_request(update: Update, context: CallbackContext):
            """Отправка запроса на аренду"""
            query = update.callback_query
            await query.answer()

            apartment_id = int(query.data.split("_")[2])
            user = update.callback_query.from_user

            client = await sync_to_async(Client.objects.filter(telegram_id=user.id).first)()
            if client:
                request = await sync_to_async(ApartmentRequest.objects.create)(
                    apartment_id=apartment_id,
                    user_telegram_id=user.id,
                    full_name=client.full_name,
                    phone_number=client.contact_number, 
                    user_username=f"@{user.username}",
                    status="IN_PROCESSING"
                )
            else :
                await query.edit_message_text("Произошла ошибка. Вы не зарегистрированы в системе.")
                return

            await query.edit_message_text("Ваш запрос на аренду отправлен владельцу квартиры.")

        async def city_filter_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()
            city_id = int(query.data.split('_')[1])
            await query.edit_message_text(
                text="Выберите район:",
                reply_markup=await district_filter_keyboard(city_id)
            )

        
        async def district_filter_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()

            district_id = int(query.data.split('_')[1])

            await query.edit_message_text(
                text="Выберите микрорайон:",
                reply_markup=await neighborhood_filter_keyboard(district_id)
            )    

        async def neighborhood_filter_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()

            neighborhood_id = int(query.data.split('_')[1])
            context.user_data["neighborhood_id"] = neighborhood_id

            await query.edit_message_text(
                text="Выберите количество комнат:",
                reply_markup=rooms_filter_keyboard()
            )


        async def rooms_filter_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()
            rooms_count = context.user_data.get("rooms_count")

            if not rooms_count:
                rooms_count = int(query.data.split('_')[1])
                context.user_data['rooms_count'] = rooms_count
                logger.info(f"rooms_count   {query.data}")

            neighborhood_id = context.user_data.get("neighborhood_id")

            if neighborhood_id is None:
                await query.edit_message_text("Ошибка: Микрорайон не выбран.")
                return

            page = int(context.user_data.get("current_page", 1))

            apartments_qs = await sync_to_async(list)(Apartment.objects.filter(neighborhood_id=neighborhood_id,is_active=True,number_of_rooms=rooms_count))
            total_apartments = len(apartments_qs)
            total_pages = (total_apartments + APARTMENTS_PER_PAGE - 1) // APARTMENTS_PER_PAGE
            start_index = (page - 1) * APARTMENTS_PER_PAGE
            end_index = start_index + APARTMENTS_PER_PAGE
            apartments = apartments_qs[start_index:end_index]

            if apartments:
                for apartment in apartments:
                    photos = await sync_to_async(lambda: list(Photo.objects.filter(apartment=apartment)))()
                    if photos:
                        media_group = [
                            InputMediaPhoto(await acreate_build_url(photo))
                            for photo in photos
                        ]

                        caption = await apartament_info(apartment)

                        await context.bot.send_media_group(chat_id=query.message.chat.id, media=media_group, caption=caption)
                        await context.bot.send_message(chat_id=query.message.chat.id, text="Выберите действие", reply_markup=InlineKeyboardMarkup([
                            apartment_request_buttons(apartment.id).inline_keyboard[0],
                            navigation_buttons().inline_keyboard[0]
                        ]))

                    else:
                        caption = await apartament_info(apartment)
                        await context.bot.send_photo(chat_id=query.message.chat.id, photo=f"{settings.DEFAULT_IMAGE_URL}", caption=caption)
                        await context.bot.send_message(chat_id=query.message.chat.id, text="Выберите действие", reply_markup=InlineKeyboardMarkup([
                            apartment_request_buttons(apartment.id).inline_keyboard[0],
                            navigation_buttons().inline_keyboard[0]
                        ]))
      
            
            else:
                await query.edit_message_text(text="Квартир по заданным параметрам не найдено.")
            
            if total_apartments>APARTMENTS_PER_PAGE:
                await context.bot.send_message(
                        chat_id=query.message.chat.id,
                        text="Выберите действие:",
                        reply_markup=generate_pagination_buttons(page, total_pages)
                    )  
                

        
        async def pagination_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()

            new_page = int(query.data.split('_')[1])

            context.user_data["current_page"] = new_page

            await rooms_filter_handler(update, context)   


        async def navigation_handler(update: Update, context: CallbackContext):
            query = update.callback_query
            await query.answer()

            data = query.data

            if data == "back":
                await query.edit_message_text(
                    text="Выберите, по какому критерию хотите отфильтровать квартиры:",
                    reply_markup=filter_menu_keyboard()
                )

            elif data == "main_menu":
                await query.edit_message_text(
                    text="Добро пожаловать! Выберите, по какому критерию хотите отфильтровать квартиры:",
                    reply_markup=filter_menu_keyboard()
                )


        async def handle_text(update: Update, context: CallbackContext):
            text = update.message.text
            if text not in ['Назад']:
                await update.message.reply_text(
                    'Неизвестная команда. Выберите одну из опций ниже.',
                    reply_markup=filter_menu_keyboard()
                )


        async def cancel(update: Update, context: CallbackContext):
            if update.message.text in ['Отмена','Назад']:
                await update.message.reply_text("Отменено.")
                await update.message.delete()
                await update.message.reply_text("Выберите дейсвтие",reply_markup=filter_menu_keyboard)
                return     


        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
                CONTACT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_number)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        application.add_handler(conv_handler)

        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Искать квартиру$'), main))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Мои данные$'), my_data))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Редактировать мои данные$'), edit_data))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Удалить мои данные$'), delete_data))
        application.add_handler(
            MessageHandler(filters.TEXT & filters.Regex('^(Имя|Контактный номер|Назад)$'),
                           handle_edit_choice))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, update_data))
        application.add_handler(CallbackQueryHandler(handle_filter_choice, pattern="^filter_"))
        application.add_handler(CallbackQueryHandler(view_apartment_details, pattern="^view_apartment_"))
        application.add_handler(CallbackQueryHandler(send_rent_request, pattern="^request_rent_"))
        application.add_handler(CallbackQueryHandler(city_filter_handler, pattern=r'^city_\d+$'))
        application.add_handler(CallbackQueryHandler(district_filter_handler, pattern=r'^district_\d+$'))
        application.add_handler(CallbackQueryHandler(neighborhood_filter_handler, pattern=r'^neighborhood_\d+$'))
        application.add_handler(CallbackQueryHandler(rooms_filter_handler, pattern=r'^rooms_\d+$'))
        application.add_handler(CallbackQueryHandler(pagination_handler, pattern=r'^page_\d+$'))
        application.add_handler(CallbackQueryHandler(navigation_handler, pattern="^(back|main_menu)$"))
        application.add_handler(CommandHandler("cancel", cancel))
        application.add_handler(MessageHandler(filters.TEXT, handle_text))

        application.run_polling()





