from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Subscription, Bot, BotSubscriptionRelation, Record


class SubscriptionsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser', email="testuser@email.com",
            password="testuser")
        self.client.login(username='testuser', password='testuser')

    def test_home_page(self):
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

        resp = self.client.get('/')
        self.assertContains(resp, 'value="4"')
