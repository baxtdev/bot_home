from asgiref.sync import sync_to_async
from bot_for_partner.models import City,District,Neighborhood
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)


def get_main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ['Мои данные', 'Редактировать мои данные'],
        ['Удалить мои данные'],
        ['Искать квартиру']
    ], one_time_keyboard=True, resize_keyboard=True)

def filter_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Город", callback_data="filter_city")],
    ])

def generate_pagination_buttons(current_page, total_pages):
    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{current_page - 1}"))

    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{current_page + 1}"))

    return InlineKeyboardMarkup([buttons])



def rooms_filter_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 комната", callback_data="rooms_1")],
        [InlineKeyboardButton("2 комнаты", callback_data="rooms_2")],
        [InlineKeyboardButton("3 комнаты", callback_data="rooms_3")],
        [InlineKeyboardButton("4+ комнаты", callback_data="rooms_4")],
    ])


async def city_filter_keyboard():
    cities = await sync_to_async(City.objects.all)() 
    buttons = [[InlineKeyboardButton(city.name, callback_data=f"city_{city.id}")] async for city in cities]
    return InlineKeyboardMarkup(buttons)

async def district_filter_keyboard(city_id):
    districts = await sync_to_async(District.objects.filter)(city_id=city_id)  
    buttons = [[InlineKeyboardButton(district.name, callback_data=f"district_{district.id}")] async for district in districts]
    
    return InlineKeyboardMarkup(buttons)

async def neighborhood_filter_keyboard(district_id):
    neighborhoods =  await sync_to_async(Neighborhood.objects.filter)(district_id=district_id)
    buttons = [[InlineKeyboardButton(neighborhood.name, callback_data=f"neighborhood_{neighborhood.id}")] async for neighborhood in neighborhoods]
    return InlineKeyboardMarkup(buttons)

def apartment_request_buttons(apartment_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить запрос на аренду", callback_data=f"request_rent_{apartment_id}")]
    ])


def navigation_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад", callback_data="back")],
        [InlineKeyboardButton("На главную", callback_data="main_menu")]
    ])