from asgiref.sync import sync_to_async

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

from ...models import Client 
from .keyboard.main import filter_menu_keyboard,get_main_menu_keyboard

NAME, CONTACT_NUMBER = range(2)



async def start(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    owner = await sync_to_async(lambda: Client.objects.filter(telegram_id=telegram_id).first())()
    if owner:
        data = (f'Вы уже зарегистрированы!\n\n'
                f'Имя: {owner.full_name}\n'
                f'Контактный номер: {owner.contact_number}\n'
                )
        
        await update.message.reply_text(data)
        await update.message.reply_text(
            'Вы можете выбрать одну из опций ниже.',
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            'Добро пожаловать! Пожалуйста, предоставьте ваше имя для регистрации в качестве клиента квартиры.'
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
    await update.message.reply_text('Все ')

    client =await sync_to_async(Client.objects.create)(
        full_name=context.user_data['name'],
        contact_number=context.user_data['contact_number'],
        telegram_id=update.message.from_user.id,
    )
    await update.message.reply_text(
                'Регистрация успешна! Вы можете выбрать одну из опций ниже.',
                reply_markup=get_main_menu_keyboard()
            )
    
    return ConversationHandler.END

async def my_data(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    owner = await sync_to_async(lambda: Client.objects.filter(telegram_id=telegram_id).first())()
    if owner:
        data = f'Имя: {owner.full_name}\nКонтактный номер: {owner.contact_number}\n'
    else:
        data = 'Ваши данные не найдены.'
    
    await update.message.reply_text(data,reply_markup=get_main_menu_keyboard())
    

async def edit_data(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Что вы хотите изменить?',
        reply_markup=ReplyKeyboardMarkup([
            ['Имя', 'Контактный номер'],
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
    
    if choice in ['Имя', 'Контактный номер']:
        await update.message.reply_text(f'Пожалуйста, предоставьте ваше новое {choice.lower()}.')
        return NAME 
    else:
        await update.message.reply_text('Неизвестный выбор. Попробуйте снова.')
        return ConversationHandler.END

async def update_data(update: Update, context: CallbackContext):
    telegram_id = update.message.from_user.id
    owner = await sync_to_async(lambda: Client.objects.filter(telegram_id=telegram_id).first())()
    if not owner:
        await update.message.reply_text('Ваши данные не найдены.')
        return ConversationHandler.END
    
    new_value = update.message.text
    choice = context.user_data.get('edit_choice')
    
    if choice == 'Имя':
        owner.full_name = new_value
    
    elif choice == 'Контактный номер':
        owner.contact_number = new_value
    
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
    owner = await sync_to_async(lambda: Client.objects.filter(telegram_id=telegram_id).first())()
    if owner:
        await sync_to_async(owner.delete)()
        await update.message.reply_text('Ваши данные удалены.')
    else:
        await update.message.reply_text('Данные не найдены.')
    await update.message.reply_text(
        'Выберите одну из опций ниже.',
        reply_markup=get_main_menu_keyboard()
    )