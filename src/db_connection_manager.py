import sqlite3
from src.Config import Config

class DatabaseConnection:

    _connection = None
    
    # plan is to create a single db connection and keep it open till the end of of execution
    #in order to avoid overhead of initializing and closing multiple connections
    
    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            cls._connection = sqlite3.connect(Config.DB_FILENAME)
        return cls._connection
    
    @classmethod
    def close_connection(cls):
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None
