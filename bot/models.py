from __future__ import unicode_literals

from calendar import monthrange, monthcalendar
from datetime import datetime

from django.db import models


class Subscription(models.Model):
    name = models.TextField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()

    def get_days(self):
        return [
            (self.monday, 1),
            (self.tuesday, 2),
            (self.wednesday, 3),
            (self.thursday, 4),
            (self.friday, 5)]

    def get_num_days_for(self, day_of_week):
        month = monthcalendar(
            datetime.now().year, datetime.now().month)
        return len([1 for i in month if i[day_of_week] != 0])

    def get_current_projected(self):
        return sum([
            self.get_num_days_for(num) for day, num in self.get_days() if day])

    def __str__(self):
        days = [name for day, name in self.get_days() if day]
        return '%(name)s %(schedule)s' % {
            'name': self.name,
            'schedule': '(%s)' % ', '.join(days) if any(days) else ''
        }


class Bot(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    def get_current_projected(self):
        return sum([
            rel.subscription.get_current_projected()
            for rel in self.botsubscriptionrelation_set.all()])

    def get_current_actuals(self):
        return sum([
            rel.get_current_actuals()
            for rel in self.botsubscriptionrelation_set.all()])


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

    def get_current_actuals(self):
        '''
        Returnsl all records for the current month
        '''
        now = datetime.now().date()
        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(
            received_at__gte=datetime(now.year, now.month, start_day),
            received_at__lte=datetime(now.year, now.month, end_day)
        ).count()

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
