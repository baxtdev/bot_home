from django.urls import path

from bot_for_partner.api import OwnerListCreateView, OwnerDetailView, OwnerDetailByTelegramView

urlpatterns = [
    path('owners/', OwnerListCreateView.as_view(), name='owner-list-create'),
    path('owners/<int:pk>/', OwnerDetailView.as_view(), name='owner-detail'),
    path('owners/telegram/<int:telegram_id>/', OwnerDetailByTelegramView.as_view(), name='owner-detail-by-telegram'),
]
