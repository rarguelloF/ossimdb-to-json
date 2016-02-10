
from models import (HostManager, InterfaceManager, MacVendorManager,
                    HostServiceManager, HostPropertyManager, NetworkManager)

from db import Db, DbConnectionError


class Alienvault:

    AvConnectionError = DbConnectionError

    def __init__(self):
        self.__db = Db()
        self.hosts = HostManager(self.__db)
        self.interfaces = InterfaceManager(self.__db)
        self.mac_vendors = MacVendorManager(self.__db)
        self.host_services = HostServiceManager(self.__db)
        self.host_properties = HostPropertyManager(self.__db)
        self.networks = NetworkManager(self.__db)

    def connect(self, host, user, pwd, db="alienvault", port=3306, timeout=5):
        """
        Create the database connection.

        @param host: database host name
        @type host: String
        @param user: database user name
        @type user: String
        @param pwd: database user password
        @type pwd: String
        @param db: database name
        @type db: String
        @param port: database listening port
        @type port: String
        """
        self.__db.connect(host, user, pwd, db, port, timeout)

    def close(self):
        """Close database connection."""
        self.__db.close()
