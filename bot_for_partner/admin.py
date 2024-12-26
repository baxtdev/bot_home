from django.contrib import admin

from bot_for_partner.models import Owner, Photo, Apartment, Neighborhood, District, City,ApartmentRequest


# Register your models here.
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email', 'address', 'telegram_id')  # Отображаемые поля в списке
    search_fields = ('name', 'contact_number', 'email', 'address', 'telegram_id')  # Поля для поиска

    # Если хотите добавить фильтрацию по полям
    list_filter = ('email',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name',)
    list_filter = ('city',)


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'district')
    search_fields = ('name',)
    list_filter = ('district',)


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('number_of_rooms', 'city', 'district', 'neighborhood', 'address', 'owner')
    search_fields = ('address', 'description')
    list_filter = ('city', 'district', 'neighborhood', 'owner')
    raw_id_fields = ('owner',)

    def save_model(self, request, obj, form, change):
        # You can add custom save logic here if needed
        super().save_model(request, obj, form, change)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'image')
    search_fields = ('apartment',)
    raw_id_fields = ('apartment',)



@admin.register(ApartmentRequest)
class ApartmentRequestAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'request_date', 'status', 'user_telegram_id', 'phone_number', 'user_username')
    search_fields = ('apartment', 'status', 'user_telegram_id', 'phone_number', 'user_username')
    
