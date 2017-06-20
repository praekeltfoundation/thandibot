from django.views.generic import ListView

from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated

from .models import Bot
from .serializers import EventSerializer


class BotListView(ListView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    model = Bot


class EventCreate(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    serializer_class = EventSerializer
