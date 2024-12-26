from asgiref.sync import sync_to_async
from ....models import City,Neighborhood,District

async def field_handler(field_name,apartament,value):
    if field_name == 'city':
        return await get_city(value)
    elif field_name == 'district':
        city = await sync_to_async(lambda:apartament.city)()
        return await get_district(value,city)
    elif field_name == 'neighborhood':
        district = await sync_to_async(lambda:apartament.district)()
        return await get_neighborhood(value,district)
    else :
        return value
    
    

async def get_city(city_name):
    return await sync_to_async(lambda: City.objects.filter(name=city_name).first())()

async def get_district(district_name, city):
    return await sync_to_async(lambda: District.objects.filter(name=district_name, city=city).first())()

async def get_neighborhood(neighborhood_name, district):
    return await sync_to_async(lambda: Neighborhood.objects.filter(name=neighborhood_name, district=district).first())()


