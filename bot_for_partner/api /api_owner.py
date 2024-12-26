# List and Create API view
from rest_framework import generics
from rest_framework.exceptions import NotFound

from bot_for_partner.models import Owner
from bot_for_partner.serializers.serializers_owner import OwnerSerializer


class OwnerListCreateView(generics.ListCreateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer


# Retrieve, Update, and Delete API view
class OwnerDetailByTelegramView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    def get_object(self):
        telegram_id = self.kwargs.get('telegram_id')
        try:
            return Owner.objects.get(telegram_id=telegram_id)
        except Owner.DoesNotExist:
            raise NotFound(detail="Owner with this Telegram ID does not exist.")
