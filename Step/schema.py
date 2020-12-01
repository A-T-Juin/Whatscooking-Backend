from graphene import relay, String, Int, Field, AbstractType, Connection, ConnectionField
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from Recipe.models import Recipe
from django.contrib.auth import get_user_model
from .models import Step
from Comment.schema import CommentNode

class CommentConnection(Connection):
    # to incorporate functionality such as total,
    # We need to create a custom connection class
    total = Int(description="Returns the amount of comments a Recipe has")

    class Meta:
        node = CommentNode

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class StepNode(DjangoObjectType):
    class Meta:
        model = Step
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'explanation': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )
    comments = ConnectionField(CommentConnection)
    total_likes = Int(description="The amount of likes per each step")

    @staticmethod
    def resolve_comments(self, context, **kwargs):
        return self.comments.all()

    @staticmethod
    def resolve_total_likes(self, context, **kwargs):
    # This will return a total amount of likes per step
        return self.amount_of_likes

class CreateStep(relay.ClientIDMutation):
    step = Field(StepNode)

    class Input:
        name = String(required=True, description="Provides a name for the step in the recipe")
        image = String(description="The url for our step's image")
        explanation = String(description="If the user wants to elaborate on the purpose of this step")
        id = Int(required=True, description="Used to pin the step to the correct recipe")
        position = Int(description="Used for identifying which step comes first/later")


    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        new_step = Step(
            name = input.get('name'),
            explanation = input.get('explanation'),
            of_recipe = Recipe.objects.get(id__exact=input.get('id')),
            position = input.get('position'),
            image = input.get('image')
        )
        new_step.save()
        return CreateStep(step=new_step)

class DeleteStep(relay.ClientIDMutation):
    step = String(description="To inform the Client that the Step instance has been deleted")

    class Input:
        step = Int(required=True, description="Used to identify the Step instance that is being deleted")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_step = Step.objects.get(id__exact=input.get('step'))
        existing_step.delete()
        return DeleteStep(step="Deleted")

class UpdateStep(relay.ClientIDMutation):
    step = Field(StepNode)

    class Input:
        id = Int(required=True, description="Used to grab the step instance that needs to be changed")
        name = String(description="Optional new name for the step")
        explanation = String(description="Optional new explanation for the step")
        position = Int(description="The position of the step in the recipe")
    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_step = Step.objects.get(id__exact=input.get('id'))
        existing_step.name = input.get('name')
        existing_step.explanation = input.get('explanation')
        existing_step.position = input.get('position')
        existing_step.save()
        return UpdateStep(step=existing_step)

class Like(relay.ClientIDMutation):
    step = Field(StepNode)

    class Input:
        step = Int(required=True, description="Identifies which Step instance is being Liked")
        user = Int(required=True, description="Uses the Client's ID to identify the user that is liking the Step")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_step = Step.objects.get(id__exact=input.get('step'))
        existing_user = get_user_model().objects.get(id__exact=input.get('user'))
        existing_step.likes.add(existing_user)
        return Like(step=existing_step)

class UnLike(relay.ClientIDMutation):
    step = Field(StepNode)

    class Input:
        step = Int(required=True, description="Identifies the Step instance that is being unliked")
        user = Int(required=True, description="Identifies the Client that is unliking the step via ID")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_step = Step.objects.get(id__exact=input.get('step'))
        existing_user = get_user_model().objects.get(id__exact=input.get('user'))
        existing_step.likes.remove(existing_user)
        return UnLike(step=existing_step)

class Query(object):
    step = relay.Node.Field(StepNode)
    all_steps = DjangoFilterConnectionField(StepNode)

class Mutation(AbstractType):
    create_step = CreateStep.Field()
    update_step = UpdateStep.Field()
    delete_step = DeleteStep.Field()
    like = Like.Field()
    un_like = UnLike.Field()
