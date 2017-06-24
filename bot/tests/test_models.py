from datetime import datetime

from django.test import TestCase

from ..models import Subscription, Bot, BotSubscriptionRelation, Record


class SubscriptionsTestCase(TestCase):

    def test_get_days_selected(self):
        mon = Subscription.objects.create(name='Monday Only', monday=True)
        self.assertEquals(mon.get_days(), [(True, 1)])

        everyday = Subscription.objects.create(
            name='Everyday', monday=True, tuesday=True, wednesday=True,
            thursday=True, friday=True)
        self.assertEquals(
            everyday.get_days(),
            [(True, 1), (True, 2), (True, 3), (True, 4), (True, 5)])

        tues_thurs = Subscription.objects.create(
            name='Tuesdays and Thursdays', tuesday=True, thursday=True)
        self.assertEquals(tues_thurs.get_days(), [(True, 2), (True, 4)])

    def test_number_of_mondays_in_may_2017(self):
        self.assertEquals(Subscription.get_num_days_for(1, 2017, 5), 5)

    def test_number_of_thursdays_in_june_2017(self):
        self.assertEquals(Subscription.get_num_days_for(4, 2017, 6), 4)

    def test_number_of_mon_in_june_2017(self):
        self.assertEquals(Subscription.get_num_days_for(4, 2017, 6), 4)

    def test_get_project_number_of_messages_for_daily_subscription(self):
        everyday = Subscription.objects.create(
            name='Everyday', monday=True, tuesday=True, wednesday=True,
            thursday=True, friday=True)
        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(everyday.get_current_month_projected(now=now), 14)

    def test_get_project_number_of_messages_for_mondays_subscription(self):
        mon = Subscription.objects.create(name='Mondays', monday=True)
        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(mon.get_current_month_projected(now=now), 3)

    def test_get_project_number_of_messages_for_tues_thurs_subscription(self):
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(tues_thurs.get_current_month_projected(now=now), 6)

    def test_get_total_projected_daily(self):
        everyday = Subscription.objects.create(
            name='Everyday', monday=True, tuesday=True, wednesday=True,
            thursday=True, friday=True)
        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(everyday.get_total_projected(now=now), 37)

    def test_get_total_projected_tuesdays(self):
        tues = Subscription.objects.create(name='Tues', tuesday=True)
        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(tues.get_total_projected(now=now), 8)


class BotTestCase(TestCase):
    def test_get_current_month_actuals_for_tues_thurs(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        bot_rel = BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs)
        # 2 records in May
        for i in [4, 11]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                received_at=datetime(2017, 5, i))

        # 4 records in June
        for i in [6, 8, 13, 15]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                received_at=datetime(2017, 6, i))

        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(bot.get_current_month_actuals(now=now), 4)

    def test_get_total_actuals_for_tues_thurs(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        bot_rel = BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs)
        # 2 records in May
        for i in [4, 11]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                received_at=datetime(2017, 5, i))

        # 4 records in June
        for i in [6, 8, 13, 15]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                received_at=datetime(2017, 6, i))

        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(bot.get_total_actuals(now=now), 6)

    def test_get_total_delivery_reports_for_tues_thurs(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        bot_rel = BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs)
        # 2 records in May
        for i in [4, 11]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                delivery_report=False,
                received_at=datetime(2017, 5, i))

        # 4 records in June
        for i in [6, 8, 13, 15]:
            Record.objects.create(
                bot_subcription_relation=bot_rel,
                message='foo',
                received_at=datetime(2017, 6, i))

        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(bot.get_total_delivery_reports(now=now), 4)
        self.assertEquals(bot.get_all_records().count(), 6)

    def test_get_total_projected_for_tues_thurs(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs)

        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(bot.get_total_projected(now=now), 15)

    def test_get_current_month_projected_for_tues_thurs(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs)

        now = datetime(2017, 6, 20)  # fix now to 20 June, 2017
        self.assertEquals(bot.get_current_month_projected(now=now), 6)
