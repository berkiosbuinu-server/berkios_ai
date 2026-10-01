import os
from berkios.persistence import Database

db = Database(os.getenv("BERKIOS_DATABASE_URL"))
db.create_all()
print("Berkios persistence schema initialized.")
