from graphene import relay, AbstractType, Boolean, String, Int, Field, List, ObjectType, Connection, ConnectionField
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from graphql_jwt.decorators import login_required
from Recipe.schema import RecipeNode
from Collection.schema import CollectionNode

class FollowerConnection(Connection):
    total = Int(description="Returns the amount of users following the Client")

    class Meta:
        abstract = True

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class FollowingConnection(Connection):
    total = Int(description="Returns the amount of users the Client is Following")

    class Meta:
        abstract = True

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class RecipeConnection(Connection):
    # to incorporate functionality such as total,
    # We need to create a custom connection class
    total = Int(description="Returns the amount of recipes a User has")

    class Meta:
        node = RecipeNode

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class CollectionConnection(Connection):
    total = Int(description="The amount of Collections the User has")

    class Meta:
        node = CollectionNode

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class UserNode(DjangoObjectType):

    class Meta:
        model = get_user_model()
        filter_fields = {
            'username': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )
        connection_class = FollowerConnection
        connection_class = FollowingConnection

    # Additional Fields
    recipes = ConnectionField(RecipeConnection)
    # We are establishing the field in our node
    # As the custom connection class we made above
    collections = ConnectionField(CollectionConnection)
    total_recipes = Int(description="Returns the total amount of recipes the user has")
    total_followers = Int(description="Returns the total amount of users that are following the user")
    total_following = Int(description="Returns the total amount of users being followed")

    @staticmethod
    def resolve_followers(self, context, **kwargs):
        return self.followers.all()

    @staticmethod
    def resolve_total_followers(self, context, **kwargs):
        return self.amount_of_followers

    @staticmethod
    def resolve_following(self, context, **kwargs):
        return self.following.all()

    @staticmethod
    def resolve_total_following(self, context, **kwargs):
        return self.amount_of_users_following

    @staticmethod
    def resolve_recipes(self, context, **kwargs):
        return self.recipes.all()

    @staticmethod
    def resolve_collections(self, context, **kwargs):
        return self.collections.all()

    @staticmethod
    def resolve_total_recipes(self, context, **kwargs):
        return len(self.recipes.all())

class FollowData(ObjectType):
    # This will be used as a container for our follow data later
    followers = Int()
    following = Int()

class CreateUser(relay.ClientIDMutation):
    user = Field(UserNode)

    class Input:
        username = String(required=True, description="Client's Username")
        email = String(required=True, description="Client's Email")
        password = String(required=True, description="Client's Password. Will not be available for Callback")
        info = String(description="Optional Field for Client's bio/info")
        image = String(description="The profile picture for the user")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        # This line is used to specify the correct User model to operate on
        User = get_user_model()
        new_user = User(
            username = input.get('username'),
            email = input.get('email'),
        )
        User.objects._create_user(
            input.get('username'),
            input.get('email'),
            input.get('password'),
            info = input.get('info'),
            image = input.get('image'),
        )
        return CreateUser(user=new_user)

class UpdateInfo(relay.ClientIDMutation):
    user = Field(UserNode)

    class Input:
        id = Int(required=True, description="ID of Client who wants to change their info")
        info = String(required=True, description="New info")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        User = get_user_model()
        id = input.get('id')
        existing_user = User.objects.get(id__exact=id)
        existing_user.info = input.get('info')
        existing_user.save()
        return UpdateInfo(user=existing_user)

class UpdateProfilePicture(relay.ClientIDMutation):
    user = Field(UserNode)

    class Input:
        username = String(required=True, description="Username of Client to identify in DB and pin picture url to")
        image = String(required=True, description="URL of image from s3")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        User = get_user_model()
        username = input.get('username')
        existing_user = User.objects.get(username__exact=username)
        existing_user.image = input.get('image')
        existing_user.save()
        return UpdateProfilePicture(user=existing_user)

# The below function is for doing server side
# Edits to the photo. If enabled, un comment
# The mutation below

# class AddPhoto(relay.ClientIDMutation):
#     success = String()
#
#     class Input:
#         id = Int(required=True, description="ID of the Client where we're pining the profile picture to")
#
#     @classmethod
#     def mutate_and_get_payload(cls, root, info, **input):
#         print("input: ", input)
#         id = input.get('id')
#         existing_user = User.objects.get(id__exact=id)
#         image = info.context.FILES['picture']
#         print("type: ", type(image))
#         image.read()
#         print("image: ", image)
#         return AddPhoto(success="True")

class Follow(relay.ClientIDMutation):
    user = Field(UserNode)

    class Input:
        individual = String(required=True, description="Client's username")
        username = String(required=True, description="The user that Client wants to follow")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        User = get_user_model()
        follower = User.objects.get(username__exact=input.get('individual'))
        user_to_follow = User.objects.get(username__exact=input.get('username'))
        follower.following.add(user_to_follow)
        return Follow(user=follower)

class UnFollow(relay.ClientIDMutation):
    user = Field(UserNode)

    class Input:
        individual = String(required=True, description="Client that will unfollow User")
        username = String(required=True, description="User being unfollowed by Client")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        User = get_user_model()
        follower = User.objects.get(username__exact=input.get('individual'))
        user_to_unfollow = User.objects.get(username__exact=input.get('username'))
        follower.following.remove(user_to_unfollow)
        return UnFollow(user=follower)


def follow_data(root, info, userID):
    User = get_user_model()
    user = User.objects.get(id__exact=userID)
    userData = FollowData(followers=user.amount_of_followers,
                            following=user.amount_of_users_following)
    return userData
# The below is used to verify the user is logged through headers
# We can enable this if we're using headers instead of passing
# Tokens as an argument

# def me(root, info):
#     user = info.context.user
#     print(type(user))
#     if user.is_anonymous:
#         raise Exception("The user is not currently logged in")
#     return user

class Query(AbstractType):
    follow_data = Field(FollowData, userID=Int(), resolver=follow_data, description="User's ID to grab followers/follows")
    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)
    follower_connection = DjangoFilterConnectionField(UserNode)
    following_connection = DjangoFilterConnectionField(UserNode)
    # The below only needs to be uncommented if the top is
    # uncommented
    # me = Field(UserNode, resolver=me, description="testing me")

    # The following will be used to test the token auth function of our application
    viewer = Field(UserNode, token=String(required=True))
    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user

class Mutation(AbstractType):
    create_user = CreateUser.Field()
    update_info = UpdateInfo.Field()
    follow_user = Follow.Field()
    unfollow_user = UnFollow.Field()
    # add_photo = AddPhoto.Field()
    # The above Field is if we want to do server side changes to
    # The photo such as resizing
    update_profile_picture = UpdateProfilePicture.Field()
