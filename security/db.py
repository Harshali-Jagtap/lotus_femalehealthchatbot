# ===== MongoDB Connection Setup using PyMongo =====
from pymongo import MongoClient


# ===== MongoDB Wrapper Class =====
class Database:
    def __init__(self, uri, database_name):
        """
        Initialize the database connection.
        :param uri: MongoDB connection URI
        :param database_name: Name of the MongoDB database to use
        """
        self.client = MongoClient(uri)
        self.database = self.client[database_name]

    def get_collection(self, collection_name):
        """
        Get a specific collection from the connected database.
        :param collection_name: The name of the collection to access
        :return: MongoDB collection object
        """
        return self.database[collection_name]


# ===== MongoDB Configuration =====
MONGO_URI = ("mongodb+srv://k00265900:1GEJF5UZmp3CGRXW@cluster0.kwssl.mongodb.net/?retryWrites=true&w=majority&appName"
             "=Cluster0")
DATABASE_NAME = "female_health_chatbot"

# ===== Instantiate the Database for Global Use =====
db_instance = Database(MONGO_URI, DATABASE_NAME)
