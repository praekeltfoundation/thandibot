import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Subscription, Bot, BotSubscriptionRelation


class SubscriptionsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser', email="testuser@email.com",
            password="testuser")
        self.client.login(username='testuser', password='testuser')

    def test_event_create(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs, urn='+27820000000')

        payload = {
            'data': {
                'message_uuid': '0000-0000-0000-0000',
                'uuid': '1111-1111-1111-1111',
                'status': 'delivered',
                'to_addr': '+27820000000',
                'timestamp': datetime(2017, 6, 20).isoformat(),
                'channel': 'sms'
            }
        }
        self.client.post(
            reverse('event-create'),
            data=json.dumps(payload), content_type='application/json')
        self.assertEquals(bot.get_total_actuals(now=datetime(2017, 6, 20)), 1)

    def test_event_create_with_invalid_channel(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs, urn='+27820000000')

        payload = {
            'data': {
                'message_uuid': '0000-0000-0000-0000',
                'uuid': '1111-1111-1111-1111',
                'status': 'delivered',
                'to_addr': '+27820000000',
                'timestamp': datetime(2017, 6, 20).isoformat(),
                'channel': 'whatsapp'
            }
        }
        response = self.client.post(
            reverse('event-create'),
            data=json.dumps(payload), content_type='application/json')
        self.assertEquals(response.status_code, 404)

    def test_event_create_duplicate_event_only_records_once(self):
        bot = Bot.objects.create(name='Mrs Test User')
        tues_thurs = Subscription.objects.create(
            name='Tuesdays, Thursdays', tuesday=True, thursday=True)
        BotSubscriptionRelation.objects.create(
            bot=bot, subscription=tues_thurs, urn='+27820000000')

        payload = {
            'data': {
                'message_uuid': '0000-0000-0000-0000',
                'uuid': '1111-1111-1111-1111',
                'status': 'delivered',
                'to_addr': '+27820000000',
                'timestamp': datetime(2017, 6, 20).isoformat(),
                'channel': 'sms'
            }
        }
        self.client.post(
            reverse('event-create'),
            data=json.dumps(payload), content_type='application/json')
        self.client.post(
            reverse('event-create'),
            data=json.dumps(payload), content_type='application/json')
        self.assertEquals(bot.get_total_actuals(now=datetime(2017, 6, 20)), 1)
