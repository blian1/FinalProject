"""
Group No: 05
Group Memners: Boyuan Lian, Maninderjit Singh, Henil Patel
Date: 2024-11-09
"""

import sqlite3

class DBCM:
    """Create a context manager for datbase operations"""
    def __init__(self, db_name="weather_data.db"):
        """Intialize instance of class."""
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Create a connection and cursor, then return the cursor."""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_trace):
        """Commit changes and close the connection."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
