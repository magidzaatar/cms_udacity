import os
#New
# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Flask secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'

    ### Azure Blob Storage Configuration ###
    BLOB_ACCOUNT = os.environ.get('BLOB_ACCOUNT') or 'ENTER_STORAGE_ACCOUNT_NAME'
    BLOB_STORAGE_KEY = os.environ.get('BLOB_STORAGE_KEY') or 'ENTER_BLOB_STORAGE_KEY'
    BLOB_CONTAINER = os.environ.get('BLOB_CONTAINER') or 'ENTER_IMAGES_CONTAINER_NAME'

    ### Azure SQL Database Configuration ###
    SQL_SERVER = os.environ.get('SQL_SERVER') or 'ENTER_SQL_SERVER_NAME.database.windows.net'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'ENTER_SQL_DB_NAME'
    SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or 'ENTER_SQL_SERVER_USERNAME'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or 'ENTER_SQL_SERVER_PASSWORD'

    # SQLAlchemy database URI (adjust driver version if needed)
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{SQL_USER_NAME}:{SQL_PASSWORD}@{SQL_SERVER}:1433/{SQL_DATABASE}"
        f"?driver=ODBC+Driver+18+for+SQL+Server"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### Microsoft Authentication Configuration ###
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET') or 'ENTER_CLIENT_SECRET_HERE'
    
    # Authority URL for multi-tenant apps (use tenant-specific URL for single-tenant apps)
    AUTHORITY = os.environ.get('AUTHORITY') or "https://login.microsoftonline.com/common"

    # Application (client) ID from Azure App Registration
    CLIENT_ID = os.environ.get('CLIENT_ID') or 'ENTER_CLIENT_ID_HERE'

    # Redirect path for OAuth2 callback
    REDIRECT_PATH = os.environ.get('REDIRECT_PATH') or "/getAToken"

    # Permissions required by the app
    SCOPE = ["User.Read"]  # Only need to read user profile for this app

    # Session type for server-side token cache
    SESSION_TYPE = "filesystem"
