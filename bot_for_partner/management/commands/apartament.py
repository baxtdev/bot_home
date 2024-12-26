from telegram import Update, ReplyKeyboardMarkup,InputMediaPhoto,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    filters,
    CallbackQueryHandler
)

from django.conf import settings
from asgiref.sync import sync_to_async

from bot_for_client.management.commands.keyboard.main import generate_pagination_buttons
from bot_for_client.management.commands.logger import logger

from ...models import Neighborhood,Apartment,District,City,Owner,Photo,ApartmentRequest
from .keyboard.main import get_main_menu_keyboard,get_cities_keyboard,\
        get_districts_keyboard,get_neighbords_keyboard,\
        create_apartment_buttons,create_field_edit_buttons,\
        get_cities_inlin_keyboard,get_apartment_list_keyboard,\
        get_apartment_requests_keyboard,get_apartment_request_keyboard,\
        get_request_action_buttons,get_count_rooms_keybord
from .text.main import apartament_info,bids_status_choices
from .handler.main import field_handler
from root.utils import acreate_build_url

ROOMS, CITY, DISTRICT, NEIGHBORHOOD, APARTMENT_ADDRESS, DESCRIPTION, CONFIRM = range(4, 11)
(PHOTOS,) = range(1)
EDIT_ADDRESS, EDIT_ROOMS, EDIT_CITY, EDIT_DISTRICT, EDIT_NEIGHBORHOOD, EDIT_DESCRIPTION = range(6)
APARTMENTS_PER_PAGE = 2

async def add_apartment(update: Update, context: CallbackContext):
    """Начало процесса добавления квартиры"""
    await update.message.reply_text('Сколько комнат в квартире?',reply_markup=get_count_rooms_keybord())
    return ROOMS

async def rooms(update: Update, context: CallbackContext):
    """Получаем количество комнат"""
    context.user_data['rooms'] = update.message.text
    await update.message.reply_text('Укажите город.',reply_markup=await get_cities_keyboard())

    return CITY

async def city(update: Update, context: CallbackContext):
    """Получаем город"""
    context.user_data['city'] = update.message.text
    await update.message.reply_text('Укажите район.',reply_markup=await get_districts_keyboard(update.message.text))
    return DISTRICT

async def district(update: Update, context: CallbackContext):
    """Получаем район"""
    context.user_data['district'] = update.message.text
    await update.message.reply_text('Укажите микрорайон.',reply_markup=await get_neighbords_keyboard(update.message.text))
    return NEIGHBORHOOD

async def neighborhood(update: Update, context: CallbackContext):
    """Получаем микрорайон"""
    context.user_data['neighborhood'] = update.message.text
    await update.message.reply_text('Укажите адрес квартиры.')
    return APARTMENT_ADDRESS

async def apartment_address(update: Update, context: CallbackContext):
    """Получаем адрес квартиры"""
    context.user_data['address'] = update.message.text
    await update.message.reply_text('Добавьте описание квартиры.')
    return DESCRIPTION

async def description(update: Update, context: CallbackContext):
    """Получаем описание"""
    context.user_data['description'] = update.message.text
    await update.message.reply_text('Подтвердите добавление квартиры. Введите "да" для подтверждения или "нет" для отмены.')
    return CONFIRM



async def confirm_apartment(update: Update, context: CallbackContext):
    """Подтверждаем и сохраняем данные в базу"""
    if update.message.text.lower() == 'да':
        telegram_id = update.message.from_user.id
        owner = await sync_to_async(lambda: Owner.objects.filter(telegram_id=telegram_id).first())()

        if owner:
            # Создаем квартиру
            city_name = context.user_data['city']
            district_name = context.user_data['district']
            neighborhood_name = context.user_data['neighborhood']

            city, _ = await sync_to_async(City.objects.get_or_create)(name=city_name)
            district, _ = await sync_to_async(District.objects.get_or_create)(name=district_name, city=city)
            neighborhood, _ = await sync_to_async(Neighborhood.objects.get_or_create)(name=neighborhood_name, district=district)

            apartment = await sync_to_async(Apartment.objects.create)(
                number_of_rooms=context.user_data['rooms'],
                city=city,
                district=district,
                neighborhood=neighborhood,
                address=context.user_data['address'],
                description=context.user_data['description'],
                owner=owner
            )
            context.user_data['apartment_id'] = apartment.id

            await update.message.reply_text('Квартира успешно добавлена. Теперь перейдем к загрузке фотографий.')
    
            return await prompt_for_photos(update, context)
        else:
            await update.message.reply_text('Ваши данные не найдены. Пожалуйста, зарегистрируйтесь сначала.')
    else:
        await update.message.reply_text('Добавление квартиры отменено.')
    
    return ConversationHandler.END


(PHOTOS,) = range(1)

async def prompt_for_photos(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Теперь загрузите фотографии для квартиры. Вы можете отправить несколько фотографий по одной.',
        reply_markup=ReplyKeyboardMarkup([['Завершить загрузку']], one_time_keyboard=True, resize_keyboard=True)
    )
    return PHOTOS

async def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]  
    apartment_id = context.user_data.get('apartment_id') 

    if apartment_id:
        photo_file = await photo.get_file()
        print(photo_file,photo)
        file_path = f'static/media/photos/{apartment_id}_{photo.file_id}.jpg'  
        img_path = f'photos/{apartment_id}_{photo.file_id}.jpg'
        await photo_file.download_to_drive(file_path)
        apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
        await sync_to_async(Photo.objects.create)(
            apartment=apartment,
            image=img_path,
            photo_id=photo.file_unique_id
        )

        await update.message.reply_text('Фотография добавлена. Вы можете загрузить ещё или нажмите "Завершить загрузку".')
    else:
        await update.message.reply_text('Ошибка: квартира не найдена.')

    return PHOTOS

async def finish_photo_upload(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Загрузка фотографий завершена. Спасибо!',
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END


async def my_apartaments(update: Update, context: CallbackContext):
    """Список своих квартир"""
    # telegram_id = update.message.from_user.id
    if update.callback_query:
        telegram_id = context._user_id

    if update.message:
        telegram_id = update.message.from_user.id

    chat_id = context._chat_id
    
        
    owner = await sync_to_async(Owner.objects.filter(telegram_id=telegram_id).first)()

    if not owner:
        await context.bot.send_message(text='Вы не зарегистрированы как владелец.',chat_id=chat_id)
        return

    page = int(context.user_data.get("current_page", 1))

    apartments_qs = await sync_to_async(lambda: list(Apartment.objects.filter(owner=owner)))()

    if not apartments_qs:
        await context.bot.send_message(text='У вас нет зарегистрированных квартир.',chat_id=chat_id)
        return


    await context.bot.send_message(text='Список ваших квартир:', parse_mode='Markdown',chat_id=chat_id)

    total_apartments = len(apartments_qs)
    total_pages = (total_apartments + APARTMENTS_PER_PAGE - 1) // APARTMENTS_PER_PAGE
    start_index = (page - 1) * APARTMENTS_PER_PAGE
    end_index = start_index + APARTMENTS_PER_PAGE
    apartments = apartments_qs[start_index:end_index]


    for apartment in apartments:
        photos = await sync_to_async(lambda: list(Photo.objects.filter(apartment=apartment)))()
        if photos:
            media_group = [
                InputMediaPhoto(await acreate_build_url(photo))
                for photo in photos
            ]

            caption = await apartament_info(apartment)

            await context.bot.send_media_group(chat_id=chat_id, media=media_group,caption=caption)
            await context.bot.send_message(text="Выберите действие:",reply_markup=await create_apartment_buttons(apartment.id),chat_id=chat_id)
        
        else:
            caption = await apartament_info(apartment)
            await context.bot.send_photo(chat_id=chat_id, photo=f"{settings.DEFAULT_IMAGE_URL}", caption=caption)
            await context.bot.send_message(text="Выберите действие:",reply_markup=await create_apartment_buttons(apartment.id),chat_id=chat_id)
    
    if total_apartments>APARTMENTS_PER_PAGE:
        await context.bot.send_message(
                    chat_id=chat_id,
                    text="Выберите действие:",
                    reply_markup=generate_pagination_buttons(page, total_pages)
                )

async def pagination_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    new_page = int(query.data.split('_')[1])
    context.user_data["current_page"] = new_page
    await my_apartaments(update, context) 


async def edit_apartment(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    apartment_id = query.data.split('_')[-1]
    
    await query.edit_message_text(text=f"Изменение квартиры с ID {apartment_id}. выберите действие",reply_markup=create_field_edit_buttons(apartment_id))

async def deactivate_apartment(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    apartment_id = query.data.split('_')[-1]

    confirmation_message = f"Вы уверены, что хотите удалить квартиру с ID {apartment_id}?"
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data=f'confirm_deactivate_apartment_{apartment_id}'),
            InlineKeyboardButton("Нет", callback_data='cancel_deactivation')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=confirmation_message, reply_markup=reply_markup)


async def to_deactivate_apartment(update: Update,contex: CallbackContext):
    query = update.callback_query
    await query.answer()
    apartment_id = query.data.split('_')[-1]
    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
    apartment.is_active = False
    await sync_to_async(apartment.save)()

    await query.edit_message_text(text=f"Квартира с ID {apartment_id} неактивировано")


async def to_activate_apartment(update: Update,contex: CallbackContext):
    query = update.callback_query
    await query.answer()
    apartment_id = query.data.split('_')[-1]
    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
    apartment.is_active = True
    await sync_to_async(apartment.save)()

    await query.edit_message_text(text=f"Квартира с ID {apartment_id} активировано")



async def confirm_deactivate_apartment(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    apartment_id = query.data.split('_')[-1]

    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
    await sync_to_async(apartment.delete)()

    await query.edit_message_text(text=f"Квартира с ID {apartment_id} успешно удалена.")


async def cancel_deactivation(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Сообщаем, что удаление отменено
    await query.edit_message_text(text="Удаление квартиры отменено.")




async def edit_field_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    _, field, apartment_id = query.data.split(":")

    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
    
    context.user_data['apartment_id'] = apartment_id
    context.user_data['edit_field'] = field

    field_names = {
        'address': 'адрес',
        'number_of_rooms': 'количество комнат',
        'city': 'город',
        'district': 'район',
        'neighborhood': 'микрорайон',
        'description': 'описание'
    }

    
    if field == 'city':
        await query.edit_message_text("Выберите город")
        await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Пожалуйста, выберите город:",
        reply_markup=await get_cities_keyboard()
        )
        return EDIT_CITY
    
    elif field == 'district':
        city = await sync_to_async(lambda: Apartment.objects.get(id=apartment_id).city)()
    
        await query.edit_message_text(f"Выберите новый район.")
        await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Пожалуйста, выберите город:",
        reply_markup=await get_districts_keyboard(city))
        return EDIT_DISTRICT
    
    elif field == 'neighborhood':
        await query.edit_message_text(f"Выберите новый микрорайон.")
        await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Пожалуйста, выберите город:",
        reply_markup=await get_neighbords_keyboard(await sync_to_async(apartment.district)())
        )
        return EDIT_NEIGHBORHOOD

    await query.edit_message_text(f"Введите новый {field_names[field]}.")

    return {
        'address': EDIT_ADDRESS,
        'number_of_rooms': EDIT_ROOMS,
        'description': EDIT_DESCRIPTION
    }[field]


async def save_new_value(update: Update, context: CallbackContext):
    field_names = {
        'address': 'адрес',
        'number_of_rooms': 'количество комнат',
        'city': 'город',
        'district': 'район',
        'neighborhood': 'микрорайон',
        'description': 'описание'
    }
    new_value = update.message.text
    apartment_id = context.user_data['apartment_id']
    field = context.user_data['edit_field']
    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)
    new_value_data = await field_handler(field,apartment,new_value)

    await sync_to_async(apartment.__setattr__)(field, new_value_data)  
    await sync_to_async(apartment.save)()

    await update.message.reply_text(f"{field_names[field].capitalize()} успешно обновлено.",reply_markup=get_main_menu_keyboard())

    return ConversationHandler.END


async def handle_request_action(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    action, request_id = query.data.split(':')
    request = await sync_to_async(ApartmentRequest.objects.get)(id=request_id)
    
    if action == 'view_request':
        await query.edit_message_text(f"Просмотр заявки:\n{request}")
    
    elif action == 'accept_request':
        request.status = 'ACCEPTED'
        await sync_to_async(request.save)()
        await query.edit_message_text("Заявка принята.")
    
    elif action == 'reject_request':
        request.status = 'REJECTED'
        await sync_to_async(request.save)()
        await query.edit_message_text("Заявка отклонена.")


async def handle_apartment_buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("view_requests_"):
        apartment_id = int(data.split("_")[2])
        
        requests = await sync_to_async(lambda: list(ApartmentRequest.objects.filter(apartment_id=apartment_id,status__in=["ACCEPTED","IN_PROCESSING"])))()

        if requests:
            for request in requests:
                message = (
                    f"Заявка на квартиру:\n"
                    f"Заявка от: {request.full_name}\n"
                    f"Телефон: {request.phone_number}\n"
                    f"Пользователь: {request.user_username}\n"
                    f"Дата заявки: {request.request_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Статус:{bids_status_choices.get(request.status)}"
                )
                if request.status in ["ACCEPTED","REJECTED"]:
                    await context.bot.send_message(chat_id=chat_id, text=message,reply_markup=get_main_menu_keyboard())
                else:
                    keyboard = get_request_action_buttons(request.id)
                    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=chat_id, text="У этой квартиры нет заявок.")

    elif data.startswith("accept_request_"):
        request_id = int(data.split("_")[2])
        request = await sync_to_async(lambda: ApartmentRequest.objects.get(id=request_id))()
        request.status = 'ACCEPTED'
        await sync_to_async(request.save)()
        await context.bot.send_message(chat_id=chat_id, text="Заявка принята.")
    
    elif data.startswith("reject_request_"):
        request_id = int(data.split("_")[2])
        request = await sync_to_async(lambda: ApartmentRequest.objects.get(id=request_id))()
        request.status = 'REJECTED'
        await sync_to_async(request.save)()
        await context.bot.send_message(chat_id=chat_id, text="Заявка отклонена.")


conv_handler_apartament = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_field_callback, pattern=r'^edit_field:')],
        states={
            EDIT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)],
            EDIT_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)],
            EDIT_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)],
            EDIT_DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)],
            EDIT_NEIGHBORHOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)],
            EDIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_new_value)]
        },
        fallbacks=[]
    )