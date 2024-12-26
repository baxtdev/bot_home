from django.conf import settings

def create_build_url(photo):
    return f"{settings.CURRENT_HOST}/media/{photo.image.name}"

async def acreate_build_url(photo):
    return f"{settings.CURRENT_HOST}/media/{photo.image.name}"