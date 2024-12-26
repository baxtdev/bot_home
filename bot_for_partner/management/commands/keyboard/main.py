from asgiref.sync import sync_to_async

from telegram import Update, ReplyKeyboardMarkup,InlineKeyboardButton, InlineKeyboardMarkup

from ....models import City,District,Neighborhood,Apartment


def get_main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ['Мои данные', 'Редактировать мои данные'],
        ['Удалить мои данные'],['Добавить Квартиру'],
        ['Мои квартиры']
    ], one_time_keyboard=True, resize_keyboard=True)

def get_apartment_request_keyboard(request_id):
    keyboard = [
        [InlineKeyboardButton("Посмотреть заявку", callback_data=f"view_request:{request_id}")],
        [InlineKeyboardButton("Принять", callback_data=f"accept_request:{request_id}")],
        [InlineKeyboardButton("Отклонить", callback_data=f"reject_request:{request_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_cities_keyboard():
    cities = await sync_to_async(lambda: list(City.objects.all()))()
    
    keyboard = []
    for city in cities:
        keyboard.append([city.name])
    
    keyboard.append(['Назад'])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def get_cities_inlin_keyboard():
    cities = await sync_to_async(lambda: list(City.objects.all()))()

    keyboard = []
    for city in cities:
        keyboard.append([InlineKeyboardButton(city.name, callback_data=f"city")])

    return InlineKeyboardMarkup(keyboard)

async def get_districts_keyboard(city_name):
    city = await sync_to_async(City.objects.get)(name=city_name)
    districts = await sync_to_async(lambda: list(District.objects.filter(city=city)))()
    
    keyboard = []
    for district in districts:
        keyboard.append([district.name])
    
    keyboard.append(['Назад', 'Город назад'])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def get_neighbords_keyboard(district_name):
    district = await sync_to_async(District.objects.get)(name=district_name)
    neighbords = await sync_to_async(lambda: list(Neighborhood.objects.filter(district=district)))()
    
    keyboard = []
    for neighborhood in neighbords:
        keyboard.append([neighborhood.name])
    
    keyboard.append(['Назад', 'Район назад', 'Город назад'])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def get_my_apartaments(user_id):
    apartments = await sync_to_async(lambda: list(Apartment.objects.filter(owner__telegram_id=user_id)))()
    
    keyboard = []
    for apartment in apartments:
        keyboard.append([apartment.address])
    
    keyboard.append(['Назад'])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)



async def create_apartment_buttons(apartment_id):
    apartment = await sync_to_async(Apartment.objects.get)(id=apartment_id)        
    buttons = [
        [InlineKeyboardButton("Изменить квартиру", callback_data=f'edit_apartment_{apartment_id}')],
        [InlineKeyboardButton("Удалить", callback_data=f'deactivate_apartment_{apartment_id}')],
        [InlineKeyboardButton("Просмотреть заявки", callback_data=f'view_requests_{apartment_id}')]
    ]

    if apartment.is_active:
        buttons.append([InlineKeyboardButton("Декативировать квартиру", callback_data=f'to_deactivate_apartment_{apartment_id}')])
    else:
        buttons.append([InlineKeyboardButton("Включить квартиру", callback_data=f'to_activate_apartment_{apartment_id}')])    
    
    return InlineKeyboardMarkup(buttons)


def create_field_edit_buttons(apartment_id):
    buttons = [
        [InlineKeyboardButton(text="Изменить адрес", callback_data=f"edit_field:address:{apartment_id}")],
        [InlineKeyboardButton(text="Изменить количество комнат", callback_data=f"edit_field:number_of_rooms:{apartment_id}")],
        [InlineKeyboardButton(text="Изменить город", callback_data=f"edit_field:city:{apartment_id}")],
        [InlineKeyboardButton(text="Изменить район", callback_data=f"edit_field:district:{apartment_id}")],
        [InlineKeyboardButton(text="Изменить микрорайон", callback_data=f"edit_field:neighborhood:{apartment_id}")],
        [InlineKeyboardButton(text="Изменить описание", callback_data=f"edit_field:description:{apartment_id}")]
    ]
    return InlineKeyboardMarkup(buttons)



def get_apartment_list_keyboard(apartments):
    keyboard = [[InlineKeyboardButton(apartment.address, callback_data=f"view_apartment_requests:{apartment.id}")]
                for apartment in apartments]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)


def get_apartment_requests_keyboard(requests):
    keyboard = [
        [InlineKeyboardButton(f"Заявка от {request.full_name}", callback_data=f"view_request:{request.id}")]
        for request in requests
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_apartment_list")])
    return InlineKeyboardMarkup(keyboard)


def get_request_action_buttons(request_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Принять заявку", callback_data=f'accept_request_{request_id}')],
        [InlineKeyboardButton("Отклонить заявку", callback_data=f'reject_request_{request_id}')]
    ])


def get_count_rooms_keybord():
    return ReplyKeyboardMarkup([
        ['1', '2', '3', '4', '5+'],
        ['Назад']
    ], one_time_keyboard=True, resize_keyboard=True)