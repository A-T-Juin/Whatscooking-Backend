from graphene import relay, String, Int, AbstractType, Field, Connection
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphene_django.filter import DjangoFilterConnectionField
from Step.models import Step
from .models import Comment

class ResponseConnection(Connection):
    # to incorporate functionality such as total,
    # We need to create a custom connection class
    total = Int(description="Returns the amount of steps a Recipe has")

    class Meta:
        abstract = True

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = {
            'text': ['exact', 'icontains', 'istartswith']
        }
        connection_class = ResponseConnection
        interfaces = (relay.Node, )

class CreateComment(relay.ClientIDMutation):
    comment = Field(CommentNode)

    class Input:
        userID = Int(required=True, description="The ID of the Client posting a comment/response")
        stepID = Int(required=True, description="The ID of the Step that the Client is commenting on")
        text = String(required=True, description="The text for the comment")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        new_comment = Comment(
            text = input.get('text'),
            posted_by = get_user_model().objects.get(id__exact=input.get('userID')),
            step_comment = Step.objects.get(id__exact=input.get('stepID'))
        )
        new_comment.save()
        return CreateComment(comment=new_comment)

class DeleteComment(relay.ClientIDMutation):
    comment = String(description="To inform the client that Comment instance has been deleted")

    class Input:
        comment = Int(required=True, description="The ID of the Comment/Response that we want to delete")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_comment = Comment.objects.get(id__exact=input.get('comment'))
        existing_comment.delete()
        return DeleteComment(comment="Deleted")

class CreateResponse(relay.ClientIDMutation):
    comment = Field(CommentNode)

    class Input:
        userID = Int(required=True, description="The ID of the Client posting a response")
        commentID = Int(required=True, description="The ID of the comment/response that the Client is commenting on")
        text = String(Required=True, description="The message the Client is relaying")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_comment = Comment.objects.get(id__exact=input.get('commentID'))
        existing_comment.responses.create(
            posted_by = get_user_model().objects.get(id__exact=input.get('userID')),
            text = input.get('text')
        )
        return CreateResponse(comment=existing_comment)

class UpdateComment(relay.ClientIDMutation):
    comment = Field(CommentNode)

    class Input:
        commentID = Int(required=True, description="Let's the Client specify which comment they want to update")
        text = String(required=True, description="The new text to replace the old comment text")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_comment = Comment.objects.get(id__exact=input.get('commentID'))
        existing_comment.text = input.get('text')
        existing_comment.save()
        return UpdateComment(comment=existing_comment)

class Query(object):
    comment = relay.Node.Field(CommentNode)
    all_comments = DjangoFilterConnectionField(CommentNode)

class Mutation(AbstractType):
    create_comment = CreateComment.Field()
    create_response = CreateResponse.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()
