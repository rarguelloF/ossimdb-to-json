
NOT_CONNECTED_ERROR = 'ERROR: Not connected to database'
MYSQLDB_NOT_INSTALLED = 'ERROR: MySQLdb is not installed on your system'


class DbConnectionError(Exception):
    pass


class Db(object):

    def __init__(self):
        try:
            self.__MySQLdb = __import__('MySQLdb')
        except ImportError:
            raise ImportError(MYSQLDB_NOT_INSTALLED)

        self.connection = None

    def close(self):
        self.__close()

    def connect(self, host, user, pwd, db, port=3306, timeout=5):
        self.__close()
        try:
            self.connection = self.__MySQLdb.connect(host=host,
                                                     port=port,
                                                     user=user,
                                                     passwd=pwd,
                                                     db=db,
                                                     connect_timeout=timeout)
        except self.__MySQLdb.OperationalError as err:
            raise DbConnectionError(err)

    def make_query(self, query, params=[]):
        if self.connection is None:
            raise Exception(NOT_CONNECTED_ERROR)

        cursor = self.connection.cursor()
        cursor.execute(query, params)

        dict_ = {
            'data': cursor.fetchall(),
            'count': int(cursor.rowcount)
        }

        return dict_

    def __close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
