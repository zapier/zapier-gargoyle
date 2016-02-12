from django.apps import AppConfig


class GargoyleAppConfig(AppConfig):
    name = 'gargoyle'
    verbose_name = 'Gargoyle'

    def ready(self):
        self.module.autodiscover()
