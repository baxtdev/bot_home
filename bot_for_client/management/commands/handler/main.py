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



