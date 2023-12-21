from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


#SQLite below:

SQLALCHEMY_DATABASE_URL='sqlite:///todosapp.db' #setting a directory to ceeate and store sqlite db file, running the code will automatically create a db file 
engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()



#postgreSQL below:

# SQLALCHEMY_DATABASE_URL='postgresql://postgres:root@localhost/db_todoapp'

# engine=create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)


# Base=declarative_base()