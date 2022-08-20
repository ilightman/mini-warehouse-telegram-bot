import os

from db_api.deta_db.db_class import DetaDB

PROJECT_KEY = os.getenv('PROJECT_KEY')
PROJECT_ID = os.getenv('PROJECT_ID')
db = DetaDB(project_key=PROJECT_KEY, project_id=PROJECT_ID)
