from django.apps import AppConfig


class BotForPartnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot_for_partner'

    def ready(self) -> None:
        import bot_for_partner.signals