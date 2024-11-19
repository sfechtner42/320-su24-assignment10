"""
Connection to context_manager
"""

from playhouse.dataset import DataSet
DB_PATH = 'databaseA10.db'

class Connection:
    """
    Creates a SQLite connection as a context manager
    """

    def __init__(self, db_path=DB_PATH):
        """
        Creates the database
        """
        self.ds = DataSet(f'sqlite:///{db_path}')
        self.user_table = None
        self.status_table = None
        self.picture_table = None

    def __enter__(self):
        """
        Establishes initial connections
        """
        self.user_table = self.ds['users']
        self.status_table = self.ds['status']
        self.picture_table = self.ds["pictures"]

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Removes the connection to the database
        """
        self.ds.close()
