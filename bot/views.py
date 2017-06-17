from django.views.generic import ListView
from .models import Bot


class BotListView(ListView):
    model = Bot
