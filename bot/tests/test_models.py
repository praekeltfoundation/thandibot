from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Subscription


# Create your tests here.
class SubscriptionsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser', email='testuser@email.com',
            password='testuser')

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
