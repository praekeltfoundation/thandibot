from __future__ import unicode_literals

from calendar import monthrange, monthcalendar
from datetime import datetime, date

from django.db import models


START_DATE = date(2017, 5, 1)


class Subscription(models.Model):
    name = models.TextField()
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)

    @classmethod
    def get_num_days_for(cls, day_of_week, y, m, now=None):
        '''
        Returns the number of times `day of week` appears in the month
        e.g there are 5 Thursdays in June 2017
        '''
        if not now:
            now = datetime.now()

        month = monthcalendar(y, m)

        return len([
            1 for i in month
            if i[day_of_week - 1] != 0 and
            date(y, m, i[day_of_week - 1]) <= now.date()])

    def get_days(self):
        return [
            (is_day, day_of_week) for is_day, day_of_week in [
                (self.monday, 1),
                (self.tuesday, 2),
                (self.wednesday, 3),
                (self.thursday, 4),
                (self.friday, 5)] if is_day]

    def get_current_month_projected(
            self, y=None, m=None, month=None, now=None):
        if not now:
            now = datetime.now()

        if not month:
            y = now.year
            m = now.month

        return sum([
            self.get_num_days_for(dow, y, m, now)
            for day, dow in self.get_days()])

    def get_total_projected(self, now=None):
        if not now:
            now = datetime.now()

        months = []
        for y in range(START_DATE.year, now.year + 1):
            for m in range(1, 13):
                if date(y, m, now.day) <= now.date() and \
                        date(y, m, now.day) >= START_DATE:
                    months.append((y, m, monthcalendar(y, m)))

        return sum(
            self.get_current_month_projected(y, m, month, now)
            for y, m, month in months)

    def __str__(self):
        days = [str(dow) for day, dow in self.get_days()]
        return '%(name)s %(schedule)s' % {
            'name': self.name,
            'schedule': '(%s)' % ', '.join(days) if any(days) else ''
        }


class Bot(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    def get_current_month_projected(self, now=None):
        if not now:
            now = datetime.now()

        return sum([
            rel.subscription.get_current_month_projected(now=now)
            for rel in self.botsubscriptionrelation_set.all()])

    def get_total_projected(self, now=None):
        if not now:
            now = datetime.now()

        return sum([
            rel.subscription.get_total_projected(now=now)
            for rel in self.botsubscriptionrelation_set.all()])

    def get_current_month_actuals(self, now=None):
        if not now:
            now = datetime.now()

        return sum([
            rel.get_current_month_actuals(now=now)
            for rel in self.botsubscriptionrelation_set.all()])

    def get_total_actuals(self, now=None):
        if not now:
            now = datetime.now()

        return sum([
            rel.get_total_actuals(now=now)
            for rel in self.botsubscriptionrelation_set.all()])

    def get_total_delivery_reports(self, now=None):
        if not now:
            now = datetime.now()

        return sum([
            rel.get_total_delivery_reports(now=now)
            for rel in self.botsubscriptionrelation_set.all()])

    def get_all_records(self):
        rel_pks = self.botsubscriptionrelation_set.all().values_list(
            'pk', flat=True)
        return Record.objects.filter(bot_subcription_relation__pk__in=rel_pks)


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

    def get_current_month_actuals(self, now=None):
        '''
        Returnsl all records for the current month
        '''
        if not now:
            now = datetime.now().date()

        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(
            received_at__gte=datetime(now.year, now.month, start_day)).count()

    def get_total_actuals(self, now=None):
        '''
        Returns all records to date
        '''
        if not now:
            now = datetime.now().date()

        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(received_at__gte=START_DATE).count()

    def get_total_delivery_reports(self, now=None):
        '''
        Returns all records to date with an affirmitive delivery report
        '''
        if not now:
            now = datetime.now().date()

        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(
            received_at__gte=START_DATE, delivery_report=True).count()

    def __str__(self):
        return '%s (%s) - %s' % (self.bot, self.channel, self.subscription)


class Record(models.Model):
    bot_subcription_relation = models.ForeignKey(BotSubscriptionRelation)
    message = models.TextField()
    record_identifier = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    received_at = models.DateTimeField()
    tries = models.IntegerField(default=1)
    delivery_report = models.BooleanField(default=True)

    @property
    def to_addr(self):
        return self.bot_subcription_relation.urn

    @property
    def channel(self):
        return self.bot_subcription_relation.channel

    def __to_js(self):
        return '{x: dow, y: time}'

    def __str__(self):
        return '%s @ %s' % (self.bot_subcription_relation, self.received_at)
