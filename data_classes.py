
# IMPORTS

class ArcSdeConnParams:
    """Parameters used for the creation of an arcpy.ArcSDESQLExecute class instance.

    Inputs:
    - conn_file: Path to an existing esri database connection file.
    - instance: the name of the SQL Server instance
    - database: the name of the database
    - login: the SQL Server login
    - password: the login password

    If **conn_file** is provided, the other inputs are not required.
    If **conn_file** is not provided, all other inputs are required.
    """

    def __init__(
            self,
            conn_file: str = '',
            instance: str = '',
            database: str = '',
            login: str = '',
            password: str = ''
    ) -> None:
        self.conn_file = conn_file
        self.instance = instance
        self.database = database
        self.login = login
        self.password = password
