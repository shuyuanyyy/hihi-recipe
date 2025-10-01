from pymongo import MongoClient
import json
from pprint import pprint
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class RecipeDatabase:
    def __init__(self, uri=None):
        # Use the provided URI or default to the one in your example
        self.uri = uri if uri else "mongodb+srv://test_user:IQ2he1ZHq3mkLJNX@cluster0.cogqyqp.mongodb.net/"
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = MongoClient(
                self.uri,
                connectTimeoutMS=30000,  # 30 seconds
                socketTimeoutMS=30000,
                retryWrites=True,
                tls=True
            )
            # Access database and collection
            self.db = self.client['recipe_database']
            self.collection = self.db['recipes']
            
            # Test connection by getting document count
            count = self.collection.count_documents({})
            print(f"Successfully connected! Found {count} recipes in the database.")
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB Atlas: {e}")
            return False
            
    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            print("Connection closed.")
            
    def find_recipe_by_id(self, recipe_id):
        """Find a recipe by its ObjectId"""
        try:
            # Convert string ID to ObjectId if needed
            if isinstance(recipe_id, str):
                recipe_id = ObjectId(recipe_id)
                
            recipe = self.collection.find_one({"_id": recipe_id})
            return recipe
        except Exception as e:
            print(f"Error finding recipe: {e}")
            return None
            
    def find_recipes(self, query={}, limit=10):
        """Find recipes matching the query"""
        try:
            recipes = list(self.collection.find(query).limit(limit))
            return recipes
        except Exception as e:
            print(f"Error finding recipes: {e}")
            return []
            
    def get_sample_recipes(self, count=5):
        """Get a sample of recipes"""
        try:
            # Use aggregation with $sample to get random documents
            pipeline = [{"$sample": {"size": count}}]
            recipes = list(self.collection.aggregate(pipeline))
            return recipes
        except Exception as e:
            print(f"Error getting sample recipes: {e}")
            return []
    
    def search_recipes_by_name(self, name_query, limit=10):
        """Search recipes by name using a text search"""
        try:
            # Case-insensitive search using regex
            query = {"name": {"$regex": name_query, "$options": "i"}}
            recipes = list(self.collection.find(query).limit(limit))
            return recipes
        except Exception as e:
            print(f"Error searching recipes: {e}")
            return []
    
    def find_recipes_by_tags(self, tags, limit=10):
        """Find recipes that contain all specified tags"""
        try:
            query = {"tags": {"$all": tags}}
            recipes = list(self.collection.find(query).limit(limit))
            return recipes
        except Exception as e:
            print(f"Error finding recipes by tags: {e}")
            return []
    
    def find_recipes_by_ingredients(self, ingredients, limit=10):
        """Find recipes that contain all specified ingredients"""
        try:
            # Create a regex pattern for each ingredient to make it case-insensitive
            ingredient_patterns = [{"ingredients": {"$regex": ingredient, "$options": "i"}} 
                                  for ingredient in ingredients]
            query = {"$and": ingredient_patterns}
            recipes = list(self.collection.find(query).limit(limit))
            return recipes
        except Exception as e:
            print(f"Error finding recipes by ingredients: {e}")
            return []
            
    def pretty_print_recipe(self, recipe):
        """Print a recipe in a readable format"""
        if not recipe:
            print("No recipe found.")
            return
            
        print(f"\n{'=' * 40}")
        print(f"Recipe: {recipe['name']}")
        print(f"{'=' * 40}")
        print(f"Cooking Time: {recipe['minutes']} minutes")
        print(f"\nDescription: {recipe['description']}")
        
        print("\nIngredients:")
        for i, ingredient in enumerate(recipe['ingredients'], 1):
            print(f"  {i}. {ingredient}")
            
        print("\nSteps:")
        for i, step in enumerate(recipe['steps'], 1):
            print(f"  {i}. {step}")
            
        print("\nNutrition Information:")
        for key, value in recipe['nutrition'].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
            
        print(f"\nTags: {', '.join(recipe['tags'])}")
        print(f"{'=' * 40}\n")
        
    def to_json(self, data):
        """Convert MongoDB data to JSON string"""
        return json.dumps(data, cls=JSONEncoder, indent=2)

# Example usage
if __name__ == "__main__":
    db = RecipeDatabase()
    if db.connect():
        # Get sample recipes
        samples = db.get_sample_recipes(3)
        print(f"Found {len(samples)} sample recipes:")
        
        # Print the first sample recipe in a readable format
        if samples:
            db.pretty_print_recipe(samples[0])
            
        # Close the connection when done
        db.close()
