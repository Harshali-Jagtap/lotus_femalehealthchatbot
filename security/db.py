from pymongo import MongoClient

class Database:
    def __init__(self, uri, database_name):
        """
        Initialize the security connection.
        """
        self.client = MongoClient(uri)
        self.database = self.client[database_name]

    def get_collection(self, collection_name):
        """
        Get a specific collection from the security.
        """
        return self.database[collection_name]


# MongoDB's connection details
MONGO_URI = ("mongodb+srv://k00265900:1GEJF5UZmp3CGRXW@cluster0.kwssl.mongodb.net/?retryWrites=true&w=majority&appName"
             "=Cluster0")
DATABASE_NAME = "female_health_chatbot"

# Create a reusable security instance
db_instance = Database(MONGO_URI, DATABASE_NAME)
