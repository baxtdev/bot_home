from ....models import Apartment
from asgiref.sync import sync_to_async

async def apartament_info(apartment:Apartment):
    district = await sync_to_async(lambda: apartment.district)()
    city = await sync_to_async(lambda: apartment.city)()
    neighborhood = await sync_to_async(lambda: apartment.neighborhood)()
    status = "Свободный" if apartment.is_active else "Занять"

    return f"""Номер:{apartment.id}\nКвартира: {apartment.address}\nОписание: {apartment.description}\nКол-во Комнат: {apartment.number_of_rooms}\nРайон: {district}\nГород: {city}\nМикрорайон: {neighborhood}\nСтатус:{status}"""


bids_status_choices = {
    "IN_PROCESSING": "Ожидание",
    "ACCEPTED": "Принято",
    "REJECTED": "Отказано",

}
