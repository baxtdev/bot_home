from telegram import Update, ReplyKeyboardMarkup,CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)
from django.conf import settings
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from bot_for_partner.models import Owner
from .apartament import *
from .keyboard.main import get_main_menu_keyboard,get_my_apartaments

# States for conversation
NAME, CONTACT_NUMBER, EMAIL, ADDRESS = range(4)



class Command(BaseCommand):
    help = 'Run the Telegram bot for registering apartment owners'

    def handle(self, *args, **kwargs):
        application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

        async def start(update: Update, context: CallbackContext):
            telegram_id = update.message.from_user.id
            owner = await sync_to_async(lambda: Owner.objects.filter(telegram_id=telegram_id).first())()
            if owner:
                data = (f'Вы уже зарегистрированы!\n\n'
                        f'Имя: {owner.name}\n'
                        f'Контактный номер: {owner.contact_number}\n'
                        f'Электронная почта: {owner.email}\n'
                        f'Адрес: {owner.address}')
                await update.message.reply_text(data)
                await update.message.reply_text(
                    'Вы можете выбрать одну из опций ниже.',
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                await update.message.reply_text(
                    'Добро пожаловать! Пожалуйста, предоставьте ваше имя для регистрации в качестве владельца квартиры.'
                )
                return NAME

        async def cancel(update: Update, context: CallbackContext):
            await update.message.reply_text('Регистрация отменена.')
            return ConversationHandler.END

        async def name(update: Update, context: CallbackContext):
            context.user_data['name'] = update.message.text
            await update.message.reply_text('Пожалуйста, предоставьте ваш контактный номер.')
            return CONTACT_NUMBER

        async def contact_number(update: Update, context: CallbackContext):
            context.user_data['contact_number'] = update.message.text
            await update.message.reply_text('Пожалуйста, предоставьте ваш адрес электронной почты.')
            return EMAIL

        async def email(update: Update, context: CallbackContext):
            context.user_data['email'] = update.message.text
            await update.message.reply_text('Пожалуйста, предоставьте ваш адрес.')
            return ADDRESS

        async def address(update: Update, context: CallbackContext):
            context.user_data['address'] = update.message.text
            telegram_id = update.message.from_user.id
            await sync_to_async(Owner.objects.create)(
                name=context.user_data['name'],
                contact_number=context.user_data['contact_number'],
                email=context.user_data['email'],
                address=context.user_data['address'],
                telegram_id=telegram_id
            )
            await update.message.reply_text(
                'Регистрация успешна! Вы можете выбрать одну из опций ниже.',
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END

        async def my_data(update: Update, context: CallbackContext):
            telegram_id = update.message.from_user.id
            owner = await sync_to_async(lambda: Owner.objects.filter(telegram_id=telegram_id).first())()
            if owner:
                data = f'Имя: {owner.name}\nКонтактный номер: {owner.contact_number}\nЭлектронная почта: {owner.email}\nАдрес: {owner.address}'
            else:
                data = 'Ваши данные не найдены.'
            await update.message.reply_text(data,reply_markup=get_main_menu_keyboard())

        async def edit_data(update: Update, context: CallbackContext):
            await update.message.reply_text(
                'Что вы хотите изменить?',
                reply_markup=ReplyKeyboardMarkup([
                    ['Имя', 'Контактный номер'],
                    ['Электронная почта', 'Адрес'],
                    ['Назад']
                ], one_time_keyboard=True, resize_keyboard=True)
            )
            return ConversationHandler.END

        async def handle_edit_choice(update: Update, context: CallbackContext):
            choice = update.message.text
            context.user_data['edit_choice'] = choice
            if choice == 'Назад':
                await update.message.reply_text(
                    'Выберите одну из опций ниже.',
                    reply_markup=get_main_menu_keyboard()
                )
                return ConversationHandler.END

            # Proceed to update data based on choice
            if choice in ['Имя', 'Контактный номер', 'Электронная почта', 'Адрес']:
                await update.message.reply_text(f'Пожалуйста, предоставьте ваше новое {choice.lower()}.')
                return NAME  # Reuse NAME state for updates; handle logic based on `edit_choice` in `update_data`
            else:
                await update.message.reply_text('Неизвестный выбор. Попробуйте снова.')
                return ConversationHandler.END

        async def update_data(update: Update, context: CallbackContext):
            telegram_id = update.message.from_user.id
            owner = await sync_to_async(lambda: Owner.objects.filter(telegram_id=telegram_id).first())()
            if not owner:
                await update.message.reply_text('Ваши данные не найдены.')
                return ConversationHandler.END

            new_value = update.message.text
            choice = context.user_data.get('edit_choice')
            if choice == 'Имя':
                owner.name = new_value
            elif choice == 'Контактный номер':
                owner.contact_number = new_value
            elif choice == 'Электронная почта':
                owner.email = new_value
            elif choice == 'Адрес':
                owner.address = new_value
            else:
                await update.message.reply_text('Неизвестный выбор. Попробуйте снова.')
                return ConversationHandler.END

            await sync_to_async(owner.save)()
            await update.message.reply_text(
                f'Ваши данные успешно обновлены. {choice.lower()} изменен(о) на: {new_value}',
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END

        async def delete_data(update: Update, context: CallbackContext):
            telegram_id = update.message.from_user.id
            owner = await sync_to_async(lambda: Owner.objects.filter(telegram_id=telegram_id).first())()
            if owner:
                await sync_to_async(owner.delete)()
                await update.message.reply_text('Ваши данные удалены.')
            else:
                await update.message.reply_text('Данные не найдены.')
            await update.message.reply_text(
                'Выберите одну из опций ниже.',
                reply_markup=get_main_menu_keyboard()
            )
            

        async def handle_text(update: Update, context: CallbackContext):
            text = update.message.text
            if text not in ['Мои данные', 'Редактировать мои данные', 'Удалить мои данные', 'Имя', 'Контактный номер',
                            'Электронная почта', 'Адрес', 'Назад']:
                await update.message.reply_text(
                    'Неизвестная команда. Выберите одну из опций ниже.',
                    reply_markup=get_main_menu_keyboard()
                )

        # Set up the conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
                CONTACT_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_number)],
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
                ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        conv_handler_add_apartment = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & filters.Regex('^Добавить Квартиру$'), add_apartment)],
            states={
                ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, rooms)],
                CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
                DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, district)],
                NEIGHBORHOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, neighborhood)],
                APARTMENT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, apartment_address)],
                DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
                CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_apartment)],
                PHOTOS: [MessageHandler(filters.PHOTO, handle_photo),
                 MessageHandler(filters.TEXT & filters.Regex('^Завершить загрузку$'), finish_photo_upload)],
            },
            fallbacks=[MessageHandler('Назад', cancel)]
        )
        application.add_handler(conv_handler)
        application.add_handler(conv_handler_add_apartment)
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Мои данные$'), my_data))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Редактировать мои данные$'), edit_data))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Удалить мои данные$'), delete_data))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Мои квартиры$'), my_apartaments))
        application.add_handler(CallbackQueryHandler(pagination_handler, pattern=r'^page_\d+$'))

        application.add_handler(CallbackQueryHandler(edit_apartment, pattern=r'^edit_apartment_'))
        application.add_handler(CallbackQueryHandler(to_deactivate_apartment, pattern=r'^to_deactivate_apartment_'))
        application.add_handler(CallbackQueryHandler(to_activate_apartment, pattern=r'^to_activate_apartment_'))
        application.add_handler(CallbackQueryHandler(deactivate_apartment, pattern=r'^deactivate_apartment_'))

        
        application.add_handler(
            MessageHandler(filters.TEXT & filters.Regex('^(Имя|Контактный номер|Электронная почта|Адрес|Назад)$'),
                           handle_edit_choice))
        application.add_handler(CallbackQueryHandler(handle_apartment_buttons, pattern=r'^view_requests_|^accept_request_|^reject_request_'))
        application.add_handler(CallbackQueryHandler(confirm_deactivate_apartment, pattern=r'^confirm_deactivate_apartment_\d+$'))
        application.add_handler(CallbackQueryHandler(cancel_deactivation, pattern='cancel_deactivation'))
    
        application.add_handler(conv_handler_apartament)
        application.add_handler(CallbackQueryHandler(handle_request_action))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, update_data))
        

        application.run_polling()
