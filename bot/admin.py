from django.contrib import admin
from .models import Bot, Subscription, BotSubscriptionRelation, Record


admin.site.register(Bot)
admin.site.register(Subscription)
admin.site.register(BotSubscriptionRelation)
admin.site.register(Record)
