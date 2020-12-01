import graphene
import graphql_jwt
import Recipe.schema
import Collection.schema
import Comment.schema
import Step.schema
import User.schema
from rx import Observable
# Testing subscription

class Subscription(graphene.ObjectType):
    # time_of_day = graphene.String()
    # def resolve_time_of_day(root, info):
    #     return Observable.

    count_seconds = graphene.Int(up_to=graphene.Int())
    def resolve_count_seconds(root, info, up_to=5):
        return Observable.interval(1000).map(lambda i: "{0}".format(i)).take_while(lambda i: int(i) <= up_to)

class Query(Recipe.schema.Query,
                Collection.schema.Query,
                Comment.schema.Query,
                Step.schema.Query,
                User.schema.Query,
                graphene.ObjectType):
    pass

class Mutation(User.schema.Mutation,
                Collection.schema.Mutation,
                Recipe.schema.Mutation,
                Step.schema.Mutation,
                Comment.schema.Mutation,
                graphene.ObjectType):
    token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
