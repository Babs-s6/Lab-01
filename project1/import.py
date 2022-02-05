import os
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

dataframe = pd.read_csv('books.csv')
for i in range(len(dataframe)):
    isbn = dataframe['isbn'][i]
    title = dataframe['title'][i].replace("'", "''")
    author = dataframe['author'][i].replace("'", "''")
    year = dataframe['year'][i]
    db.execute(f"INSERT INTO books(isbn, title, author, year) values ('{isbn}', '{title}', '{author}', {year})")

db.commit()

print("Done.")
