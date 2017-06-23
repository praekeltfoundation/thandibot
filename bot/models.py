from __future__ import unicode_literals

from calendar import monthrange, monthcalendar
from datetime import datetime, date

from django.db import models


START_DATE = date(2017, 5, 1)


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
        Returns the number of times `day of week` appears in the month
        e.g there are 5 Thursdays in June 2017
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
        now = datetime.now().date()
        for y in range(START_DATE.year, datetime.now().year + 1):
            for m in range(1, 13):
                if date(y, m, now.day) <= now and \
                        date(y, m, now.day) >= START_DATE:
                    months.append((y, m, monthcalendar(y, m)))

        return sum(
            self.get_current_projected(y, m, month) for y, m, month in months)

    def __str__(self):
        days = [str(dow) for day, dow in self.get_days() if day]
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

    def get_total_actuals(self):
        return sum([
            rel.get_total_actuals()
            for rel in self.botsubscriptionrelation_set.all()])

    def get_total_delivery_reports(self):
        return sum([
            rel.get_total_delivery_reports()
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

    def get_current_actuals(self):
        '''
        Returnsl all records for the current month
        '''
        now = datetime.now().date()
        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(
            received_at__gte=datetime(now.year, now.month, start_day)).count()

    def get_total_actuals(self):
        '''
        Returns all records to date
        '''
        now = datetime.now().date()
        start_day, end_day = monthrange(now.year, now.month)
        return self.record_set.filter(received_at__gte=START_DATE).count()

    def get_total_delivery_reports(self):
        '''
        Returns all records to date with an affirmitive delivery report
        '''
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
