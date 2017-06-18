from __future__ import unicode_literals

from calendar import monthrange, monthcalendar
from datetime import datetime, date

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

    def get_num_days_for(self, day_of_week, y, m, month):
        '''
        TODO: exclude days greater than `now()`
        '''
        return len([
            1 for i in month
            if i[day_of_week] != 0 and
            date(y, m, i[day_of_week]) <= datetime.now().date()])

    def get_current_projected(self, y=None, m=None, month=None):
        if not month:
            y = datetime.now().year
            m = datetime.now().month
            month = monthcalendar(y, m)
        return sum([
            self.get_num_days_for(dow, y, m, month)
            for day, dow in self.get_days() if day])

    def get_total_projected(self):
        months = []
        start_date = date(2017, 5, 1)
        now = datetime.now().date()
        for y in range(start_date.year, datetime.now().year + 1):
            for m in range(1, 13):
                if date(y, m, now.day) <= now and \
                        date(y, m, now.day) >= start_date:
                    months.append((y, m, monthcalendar(y, m)))

        return sum(
            self.get_current_projected(y, m, month) for y, m, month in months)

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

    def get_total_projected(self):
        return sum([
            rel.subscription.get_total_projected()
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
