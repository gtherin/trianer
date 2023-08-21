import shelve
from pydantic import BaseModel


class PersistentSettings(BaseModel):
    """
    This pydantic model will try to initialize itself from the database upon every instantiation
    It further supplies an update function, that allows to write back any changes into the database, under its key.
    """

    def __init__(self, **data):
        with shelve.open("config.db") as db:
            super().__init__(**db.get("settings", default={}), **data)

    def update(self):
        """
        Persist the pydantic-dict that represents the model
        """
        with shelve.open("config.db") as db:
            db["settings"] = self.dict()
