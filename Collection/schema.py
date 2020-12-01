from graphene import relay, Field, String, AbstractType, Int, Connection, ConnectionField
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Collection
from django.contrib.auth import get_user_model
from User.models import User
from Recipe.models import Recipe
from Recipe.schema import RecipeNode

class CollectionRecipeConnection(Connection):
    total = Int(description="The amount of recipes in this collection of Recipes")

    class Meta:
        node = RecipeNode

    def resolve_total(self, context, **kwargs):
        return self.iterable.count()

class CollectionNode(DjangoObjectType):
    class Meta:
        model = Collection
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'info': ['icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )

    recipes = ConnectionField(CollectionRecipeConnection)

    @staticmethod
    def resolve_recipes(self, context, **kwargs):
        return self.recipes.all()

class CreateCollection(relay.ClientIDMutation):
    collection = Field(CollectionNode)

    class Input:
        name = String(required=True, description="Name of the Collection of Recipes")
        info = String(description="Optional description of the Collection")
        owner = String(required=True, description="Username of Client creating the Collection")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        print("input: ", input)
        new_collection = Collection(
            name = input.get('name'),
            info = input.get('info'),
            owned_by = get_user_model().objects.get(username__exact=input.get('owner'))
        )
        new_collection.save()
        return CreateCollection(collection=new_collection)

class UpdateCollection(relay.ClientIDMutation):
    collection = Field(CollectionNode)

    class Input:
        id = Int(required=True, description="The ID of the Collection")
        name = String(description="The string that the Client wants to change their Collection name to")
        info = String(description="The string that the Client wants to change their info to")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_collection = Collection.objects.get(id__exact=input.get('id'))
        existing_collection.name = input.get('name')
        existing_collection.info = input.get('info')
        existing_collection.save()
        return UpdateCollection(collection=existing_collection)

class DeleteCollection(relay.ClientIDMutation):
    collection = String(description="To inform the client that the Collection instance has been successfully deleted")

    class Input:
        collection = Int(required=True, description="The ID of the collection that is being deleted")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_collection = Collection.objects.get(id__exact=input.get('collection'))
        existing_collection.delete()
        return DeleteCollection(collection="Deleted")

class AddRecipeToCollection(relay.ClientIDMutation):
    collection = Field(CollectionNode)

    class Input:
        collection = Int(required=True, description="The collection we want to add the recipe to")
        recipeID = Int(required=True, description="The ID of the recipe we're trying to add to the collection")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_collection = Collection.objects.get(id__exact=input.get('collection'))
        recipe_to_add = Recipe.objects.get(id__exact=input.get('recipeID'))
        existing_collection.recipes.add(recipe_to_add)
        return AddRecipeToCollection(collection=existing_collection)

class RemoveRecipeFromCollection(relay.ClientIDMutation):
    collection = Field(CollectionNode)

    class Input:
        collection = Int(required=True, description="The collection from which the recipe is to be removed")
        recipeID = Int(required=True, description="The recipe in which we want to remove from the collection")

    @classmethod
    def mutate_and_get_payload(cls, root, _info, **input):
        existing_collection = Collection.objects.get(id__exact=input.get('collection'))
        recipe_to_remove = Recipe.objects.get(id__exact=input.get('recipeID'))
        existing_collection.recipes.remove(recipe_to_remove)
        return RemoveRecipeFromCollection(collection=existing_collection)

class Query(object):
    collection = relay.Node.Field(CollectionNode)
    all_collections = DjangoFilterConnectionField(CollectionNode)

class Mutation(AbstractType):
    create_collection = CreateCollection.Field()
    update_collection = UpdateCollection.Field()
    delete_collection = DeleteCollection.Field()
    add_recipe_to_collection = AddRecipeToCollection.Field()
    remove_recipe_from_collection = RemoveRecipeFromCollection.Field()
