import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth.models import User
import graphql_jwt
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_jwt.decorators import login_required
from .models import Profile, Message
from graphql_relay import from_global_id


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['exact', 'icontains'],
        }
        interfaces = (relay.Node,)


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'user_prof__username': ['icontains'],
        }
        interfaces = (relay.Node,)


class MessageNode(DjangoObjectType):
    class Meta:
        model = Message
        filter_fields = {
            'sender': ['exact'],
            'receiver': ['exact'],
        }
        interfaces = (relay.Node,)


class CreateUserMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate_and_get_payload(root, info, **input):
        user = User(
            username=input.get('username'),
            email=input.get('email'),
        )
        user.set_password(input.get('password'))
        user.save()

        return CreateUserMutation(user=user)


class CreateProfileMutation(relay.ClientIDMutation):
    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile(
            user_prof_id=info.context.user.id,
        )
        profile.save()

        return CreateProfileMutation(profile=profile)


class CreateMessageMutation(relay.ClientIDMutation):
    class Input:
        message = graphene.String(required=True)
        receiver = graphene.ID(required=True)

    message = graphene.Field(MessageNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        message = Message(
            message=input.get('message'),
            sender_id=info.context.user.id,
            receiver_id=from_global_id(input.get('receiver'))[1]
        )
        message.save()
        return CreateMessageMutation(message=message)


class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        friends = graphene.List(graphene.ID)
        friend_requests = graphene.List(graphene.ID)

    profile = graphene.Field(ProfileNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        profile = Profile.objects.get(id=from_global_id(input.get('id'))[1])
        if input.get('friends') is not None:
            friends_set = []
            for fri in input.get('friends'):
                friends_id = from_global_id(fri)[1]
                friends_object = User.objects.get(id=friends_id)
                friends_set.append(friends_object)
            profile.friends.set(friends_set)

        if input.get('friend_requests') is not None:
            friend_requests_set = []
            for fri in input.get('friend_requests'):
                friend_requests_id = from_global_id(fri)[1]
                friend_requests_object = User.objects.get(id=friend_requests_id)
                friend_requests_set.append(friend_requests_object)
            profile.friend_requests.set(friend_requests_set)

        profile.save()

        return UpdateProfileMutation(profile=profile)


class Mutation(graphene.AbstractType):
    create_user = CreateUserMutation.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    create_profile = CreateProfileMutation.Field()
    update_profile = UpdateProfileMutation.Field()
    create_message = CreateMessageMutation.Field()


class Query(graphene.ObjectType):
    profile = graphene.Field(ProfileNode)
    all_users = DjangoFilterConnectionField(UserNode)
    all_profiles = DjangoFilterConnectionField(ProfileNode)
    all_messages = DjangoFilterConnectionField(MessageNode)

    @login_required
    def resolve_profile(self, info, **kwargs):
        return Profile.objects.get(user_prof=info.context.user.id)

    @login_required
    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    @login_required
    def resolve_all_profiles(self, info, **kwargs):
        return Profile.objects.all()

    @login_required
    def resolve_all_messages(self, info, **kwargs):
        return Message.objects.all()
