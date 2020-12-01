from . import utils
from graphene import relay, String, Int, AbstractType, Field, ObjectType, Connection, ConnectionField
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphene_django.filter import DjangoFilterConnectionField
from .models import Recipe
from Step.schema import StepNode

class StepConnection(Connection):
    # to incorporate functionality such as total,
    # We need to create a custom connection class
    total = Int(description="Returns the amount of steps a Recipe has")

    class Meta:
        node = StepNode

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()


class RecipeNode(DjangoObjectType):
    class Meta:
        model = Recipe
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'tags': ['icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )
    steps = ConnectionField(StepConnection)
    likes = Int(description="The amount of likes for each Recipe")
    comments = Int(description="The total amount of comments")
    difficulty_level = String(description="Returns the difficulty level in a human-readable Form")
    # This creates a field in the RecipeNode that we can call
    # Using the staticmethod

    @staticmethod
    def resolve_steps(self, context, **kwargs):
        return self.steps.all()

    @staticmethod
    def resolve_likes(self, context, **kwargs):
        return self.amount_of_likes

    @staticmethod
    def resolve_comments(self, context, **kwargs):
        return self.total_comments

    @staticmethod
    def resolve_difficulty_level(self, context, **kwargs):
        return self.difficulty_level

class LikeData(ObjectType):
    # This will be used as a container for returning our like data
    likes = Int()

class CreateRecipe(relay.ClientIDMutation):
    recipe = Field(RecipeNode)

    class Input:
        name = String(required=True, description="The name of the recipe being created")
        image = String(required=True, description="The image that will be used for the recipe (Shown in the discover area)")
        tags = String(required=True, description="A list of tags that will be used to allow search functionality later")
        description = String(required=True, description="A description of the Recipe if further clarification is wanted")
        difficulty = String(required=True, description="States how difficult the Recipe will be. Comes in 'Easy', 'Fair', 'Hard', and 'Challenging'")
        ingredients = String(required=True, description="User will input a string of necessary ingredients separated by a comma (,)")
        time = Int(required=True, description="User will state the amount of time required to complete the Recipe")
        servings = Int(required=True, description="User will state how many servings are created per recipe")
        owner = String(required=True, description="The username of the Client creating the Recipe")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        print("input: ", input)
        print("tags: ", utils.parseTags(input.get('tags')))
        # for our tag cleaner to work, the tags *MUST* be separated
        # by commas
        # for our ingredient cleaner to work, the ingredients *MUST* be separated
        # by commas

        tags = utils.parseTags(input.get('tags'))
        ingredients = utils.ingredient_cleaner(input.get('ingredients'))
        new_recipe = Recipe(
            name = input.get('name'),
            image = input.get('image'),
            tags = tags,
            description = input.get('description'),
            difficulty = input.get('difficulty'),
            ingredients = ingredients,
            time = input.get('time'),
            servings = input.get('servings'),
            created_by = get_user_model().objects.get(username__exact=input.get('owner')),
        )
        new_recipe.save()
        return CreateRecipe(recipe=new_recipe)

class DeleteRecipe(relay.ClientIDMutation):
    recipe = String(description="To inform the Client that the Recipe instance is deleted")

    class Input:
        recipe = Int(required=True, description="The ID used to identify the Recipe instance to be deleted")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_recipe = Recipe.objects.get(id__exact=input.get('recipe'))
        existing_recipe.delete()
        return DeleteRecipe(recipe="Deleted")

class UpdateRecipe(relay.ClientIDMutation):
    recipe = Field(RecipeNode)

    class Input:
        id = Int(required=True, description="Recipe ID that will be used for lookup in the DB")
        name = String(required=True, description="The name of the recipe being created")
        image = String(required=True, description="The image that will be used for the recipe (Shown in the discover area)")
        tags = String(required=True, description="A list of tags that will be used to allow search functionality later")
        description = String(required=True, description="A description of the Recipe if further clarification is wanted")
        difficulty = String(required=True, description="States how difficult the Recipe will be. Comes in 'Easy', 'Fair', 'Hard', and 'Challenging'")
        ingredients = String(required=True, description="User will input a string of necessary ingredients separated by a comma (,)")
        time = Int(required=True, description="User will state the amount of time required to complete the Recipe")
        servings = Int(required=True, description="User will state how many servings are created per recipe")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        tags = utils.parseTags(input.get('tags'))
        ingredients = utils.ingredient_cleaner(input.get('ingredients'))

        existing_recipe = Recipe.objects.get(id__exact=input.get('id'))
        existing_recipe.name = input.get('name')
        existing_recipe.image = input.get('image')
        existing_recipe.tags = tags
        existing_recipe.description = input.get('description')
        existing_recipe.difficulty = input.get('difficulty')
        existing_recipe.ingredients = ingredients
        existing_recipe.time = input.get('time')
        existing_recipe.save()
        return UpdateRecipe(recipe=existing_recipe)

def like_data(root, info, recipeID):
    recipe = Recipe.objects.get(id__exact=recipeID)
    recipe_likes = LikeData(likes=recipe.amount_of_likes)
    return recipe_likes

class Query(object):
    total_likes = Field(LikeData, recipeID=Int(), resolver=like_data)
    recipe = relay.Node.Field(RecipeNode)
    all_recipes = DjangoFilterConnectionField(RecipeNode)

class Mutation(AbstractType):
    create_recipe = CreateRecipe.Field()
    update_recipe = UpdateRecipe.Field()
    delete_recipe = DeleteRecipe.Field()
