from __future__ import absolute_import

import unittest

from ossimdb_to_json.db import Db as AvDb
from ossimdb_to_json.db import DbConnectionError

# Configure your testing database here.
HOST = 'X.X.X.X'
USER = 'user'
PWD = 'password'
DB = 'alienvault'


class DbTest(unittest.TestCase):
    """Test basic database connection and queries."""

    @classmethod
    def setUpClass(self):
        self._connection = AvDb()
        self._connection.connect(HOST, USER, PWD, DB)

    @classmethod
    def tearDownClass(self):
        self._connection.close()

    def test_can_fetch_data(self):
        """Test we can fetch data from database."""
        query = "SELECT * FROM host_ip;"

        data = self._connection.make_query(query)
        self.assertNotEqual(data['count'], 0)

    def test_queries_params_work(self):
        """Test we can fetch data from database using prepared statements."""
        query = ("SELECT hex(host_id) AS id "
                 "FROM host_ip "
                 "WHERE hex(host_id) = %s;")
        params = ("2949A99CA33F11E5881D000CE21AE882", )

        data = self._connection.make_query(query, params)
        self.assertNotEqual(data['count'], 0)

    def test_throw_connect_exception(self):
        """Test we throw a valid exception when we can't connect to MySQL."""
        connection = AvDb()
        non_valid_host = "192.168.2.2"

        self.assertRaises(DbConnectionError,
                          connection.connect,
                          non_valid_host,
                          USER,
                          PWD,
                          DB,
                          timeout=5)

if __name__ == '__main__':
    unittest.main()
