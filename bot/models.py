from __future__ import unicode_literals

from django.db import models


class Subscription(models.Model):
    name = models.TextField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()

    def __str__(self):
        days = [name for day, name in [
            (self.monday, 'm'),
            (self.tuesday, 't'),
            (self.wednesday, 'w'),
            (self.thursday, 't'),
            (self.friday, 'f')] if day]
        return '%(name)s %(schedule)s' % {
            'name': self.name,
            'schedule': '(%s)' % ', '.join(days) if any(days) else ''
        }


class Bot(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class BotSubscriptionRelation(models.Model):
    SMS = 'sms'
    WHATSAPP = 'whatsapp'
    CHANNELS = (
        (SMS, 'SMS'),
        (WHATSAPP, 'WhatsApp'),
    )
    bot = models.ForeignKey(Bot)
    subscription = models.ForeignKey(Subscription)
    channel = models.CharField(
        max_length=128, choices=CHANNELS, blank=True, null=True, default=SMS)
    urn = models.CharField(max_length=128, blank=True)
    selected_language = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '%s (%s) - %s' % (self.bot, self.channel, self.subscription)


class Record(models.Model):
    bot_subcription_relation = models.ForeignKey(BotSubscriptionRelation)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    received_at = models.DateTimeField()
    tries = models.IntegerField(default=1)
    delivery_report = models.BooleanField(default=True)

    def __str__(self):
        return '%s @ %s' % (self.bot_subcription_relation, self.received_at)
