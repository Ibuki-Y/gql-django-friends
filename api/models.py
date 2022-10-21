from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user_prof = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE,
    )
    friends = models.ManyToManyField(
        User,
        related_name='profiles_friends',
        blank=True,
    )
    friend_requests = models.ManyToManyField(
        User,
        related_name='profiles_friend_requests',
        blank=True,
    )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_prof.username


class Message(models.Model):
    message = models.CharField(max_length=140)
    sender = models.ForeignKey(
        User,
        related_name='message_sender',
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        User,
        related_name='message_receiver',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.id)
