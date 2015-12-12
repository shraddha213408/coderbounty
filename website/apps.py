from django.apps import AppConfig
from actstream import registry
from django.contrib.auth.models import User
from website.models import Bounty, Solution, Taker

class WebsiteConfig(AppConfig):
    name = 'website'

    def ready(self):
        registry.register(self.get_model('Issue'))
        registry.register(User)
        registry.register(Bounty)
        registry.register(Solution)