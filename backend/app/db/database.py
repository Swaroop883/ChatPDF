from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL
# engine is responsible for telling the sessionmaker which databse to connet
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# sessionmaker is the factory for creating new Session objects, which are used to interact with the database. It is configured with the engine to know which database to connect to , for every single request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Declarative base is the class that contains all the blueprints of the tables that need to be created in the database for this application , in its metadata


#pass only exists to get inherited from
class Base(DeclarativeBase):
    pass


# instead of writing this everytime in every route , because each request will start new session we wrote here once for all the routed and we need to close the session after the request is completed, so we use try and finally to ensure that the session is closed after the request is completed.
def get_db():
    db = SessionLocal() 
    try:
        # at this point yield pauses here anf hands over the db to the router and returns here after the router complets its work , and after is resumes its code in tht get_db again to execute the finally
        yield db
    finally:
        db.close()
