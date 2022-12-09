from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import config
from repository.alchemy_tables import metadata

engine = create_engine(url=config.database_url)

session = Session(engine)
