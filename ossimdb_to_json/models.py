

class AbstractObjectManager(object):
    """Common functions used by all ObjectManagers."""

    def __init__(self, db):
        self.__db = db
        self.query = ''
        # Used for prepared statements
        self.filter_values = []

    def all(self):
        """Return all objects."""
        if type(self) == AbstractObjectManager:
            raise NotImplementedError

        self.query = "SELECT {} FROM {}{};".format(
            self._fields, self._columns, self._joins)
        self.filter_values = []

        return self

    def filter(self, **kwargs):
        """Filter query."""
        if type(self) == AbstractObjectManager:
            raise NotImplementedError

        kwargs = {k: v for k, v in kwargs.iteritems() if v is not None}

        if not kwargs:
            raise ValueError

        conditions, values = self._conditions(**kwargs)

        self.query = "SELECT {} FROM {}{}{};".format(
            self._fields, self._columns, self._joins, conditions)
        self.filter_values = values

        return self

    def get(self, pk):
        """Get object by primary key."""
        return self.filter(pk=pk)

    def result(self):
        """Return query results as a list of dicts."""
        result = []
        data = self.__db.make_query(self.query, self.filter_values)['data']

        for item in data:
            result.append(self.as_dict(item))

        return result


class HostManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        super(HostManager, self).__init__(*args, **kwargs)

    @staticmethod
    def as_dict(item):
        """Translate Alienvault MySQL query result to dict."""
        dict_ = {
            'id': item[0],
            'hostname': item[1],
            'domain': item[2],
            'asset_priority': item[3],
            'lon': item[4],
            'lat': item[5],
            'country': item[6],
            'description': item[7]
        }

        return dict_

    def _conditions(self, pk=None, ip=None, mac=None, iface=None):

        no_conditions = not (pk or ip or mac or iface)

        if no_conditions:
            return ""

        if mac:
            mac = mac.replace(":", "")
            mac = mac.upper()

        conditions_dict = {
            pk: "host.id = UNHEX(%s)",
            ip: "host_ip.ip = UNHEX(CONV(INET_ATON(%s),10,16))",
            mac: "host_ip.mac = UNHEX(%s)",
            iface: "host_ip.interface = %s"
        }

        query_conditions = [conditions_dict[key] for key in (pk, ip, mac, iface)
                            if key is not None]
        condition_values = [key for key in (pk, ip, mac, iface)
                            if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):

        query_fields = (
            "HEX(host.id) AS id",
            "host.hostname AS hostname",
            "host.fqdns AS domain",
            "host.asset AS asset_priority",
            "host.lon AS lon",
            "host.lat AS lat",
            "host.country AS country",
            "host.descr AS descr"
        )

        return ", ".join(query_fields)

    def __columns(self):

        query_columns = (
            "host",
        )

        return ", ".join(query_columns)

    def __joins(self):

        query_joins = (
            "host_ip ON host.id = host_ip.host_id",
        )

        return " INNER JOIN {}".format(" ".join(query_joins))


class InterfaceManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        self.mac_vendors = MacVendorManager(*args, **kwargs)

        super(InterfaceManager, self).__init__(*args, **kwargs)

    def as_dict(self, item):
        """Translate Alienvault MySQL query result to dict."""
        mac_ = item[2]
        mac_vendor = None

        if mac_:
            mac_ = ":".join([mac_[i:i + 2] for i in range(0, len(mac_), 2)])
            mac_vendor = self.mac_vendors.filter(mac=mac_).result()

        if mac_vendor:
            mac_vendor = mac_vendor[0]['vendor']
        else:
            mac_vendor = ''

        dict_ = {
            'iface_name': item[0],
            'ip': item[1],
            'mac': mac_,
            'mac_vendor': mac_vendor,
        }

        return dict_

    def _conditions(self, pk=None, ip=None, mac=None, iface=None):
        if mac:
            mac = mac.replace(":", "")
            mac = mac.upper()

        conditions_dict = {
            pk: "host_ip.host_id = UNHEX(%s)",
            ip: "host_ip.ip = UNHEX(CONV(INET_ATON(%s),10,16))",
            mac: "host_ip.mac = UNHEX(%s)",
            iface: "host_ip.interface = %s"
        }

        query_conditions = [conditions_dict[key] for key in (pk, ip, mac, iface)
                            if key is not None]
        condition_values = [key for key in (pk, ip, mac, iface)
                            if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):
        query_fields = (
            "host_ip.interface AS interface",
            "INET_NTOA(CONV(HEX(host_ip.ip), 16, 10)) AS ip",
            "HEX(host_ip.mac) AS mac",
        )

        return ", ".join(query_fields)

    def __columns(self):
        query_columns = (
            "host_ip",
        )

        return ", ".join(query_columns)

    def __joins(self):
        return ""


class MacVendorManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        super(MacVendorManager, self).__init__(*args, **kwargs)

    @staticmethod
    def as_dict(item):
        """Translate Alienvault MySQL query result to dict."""
        mac = item[0]
        if mac:
            mac = ":".join([mac[i:i + 2] for i in range(0, len(mac), 2)])

        dict_ = {
            'mac_prefix': mac,
            'vendor': item[1]
        }

        return dict_

    def _conditions(self, mac=None, vendor=None):
        if mac:
            mac = mac.replace(":", "")
            mac = mac.upper()
            mac = mac[:3]

        conditions_dict = {
            mac: "host_mac_vendors.mac = UNHEX(%s)",
            vendor: "host_mac_vendors.vendor = %s"
        }

        query_conditions = [conditions_dict[key] for key in (mac, vendor)
                            if key is not None]
        condition_values = [key for key in (mac, vendor)
                            if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):
        query_fields = (
            "HEX(host_mac_vendors.mac) AS mac_prefix",
            "host_mac_vendors.vendor AS vendor"
        )

        return ", ".join(query_fields)

    def __columns(self):
        query_columns = (
            "host_mac_vendors",
        )

        return ", ".join(query_columns)

    def __joins(self):
        return ""


class HostPropertyManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        super(HostPropertyManager, self).__init__(*args, **kwargs)

    @staticmethod
    def as_dict(item):
        """Translate Alienvault MySQL query result to dict."""
        dict_ = {
            'name': item[0],
            'description': item[1],
            'value': item[2],
            'extra': item[3]
        }

        return dict_

    def _conditions(self, pk=None, property_ref=None, name=None, value=None):
        conditions_dict = {
            pk: "host_properties.host_id = UNHEX(%s)",
            property_ref: "host_properties.property_ref = %s",
            name: "host_property_reference.name = %s",
            value: "host_properties.value = %s"
        }

        query_conditions = [conditions_dict[key] for key in
                            (pk, property_ref, name, value)
                            if key is not None]
        condition_values = [key for key in
                            (pk, property_ref, name, value)
                            if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):
        query_fields = (
            "host_property_reference.name AS name",
            "host_property_reference.description AS description",
            "host_properties.value AS value",
            "host_properties.extra AS extra"
        )

        return ", ".join(query_fields)

    def __columns(self):
        query_columns = (
            "host_properties",
        )

        return ", ".join(query_columns)

    def __joins(self):
        query_joins = (
            "host_property_reference ON host_properties.property_ref = host_property_reference.id",
        )

        return " INNER JOIN {}".format(" ".join(query_joins))


class HostServiceManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        super(HostServiceManager, self).__init__(*args, **kwargs)

    def as_dict(self, item):
        """Translate Alienvault MySQL query result to dict."""
        av_protocol = str(item[2])

        # Translate from Alienvault format to human-readable
        if av_protocol == '6':
            protocol = 'tcp'
        else:
            protocol = 'udp'

        dict_ = {
            'ip': item[0],
            'port': str(item[1]),
            'protocol': protocol,
            'service': item[3],
            'version': item[4]
        }

        return dict_

    def _conditions(self, pk=None, ip=None, port=None, protocol=None,
                    service=None, version=None):
        conditions_dict = {
            pk: "host_services.host_id = UNHEX(%s)",
            ip: "host_services.host_ip = UNHEX(CONV(INET_ATON(%s),10,16))",
            port: "host_services.port = %s",
            protocol: "host_services.protocol = %s",
            service: "host_services.service = %s",
            version: "host_services.version = %s",
        }

        keys = (pk, ip, port, protocol, service, version)

        query_conditions = [conditions_dict[key] for key in keys
                            if key is not None]
        condition_values = [key for key in keys if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):
        query_fields = (
            "INET_NTOA(CONV(HEX(host_services.host_ip), 16, 10)) AS ip",
            "host_services.port AS port",
            "host_services.protocol AS protocol",
            "host_services.service AS service",
            "host_services.version AS version"
        )

        return ", ".join(query_fields)

    def __columns(self):
        query_columns = (
            "host_services",
        )

        return ", ".join(query_columns)

    def __joins(self):
        return ""


class NetworkManager(AbstractObjectManager):

    def __init__(self, *args, **kwargs):
        self._fields = self.__fields()
        self._columns = self.__columns()
        self._joins = self.__joins()

        super(NetworkManager, self).__init__(*args, **kwargs)

    @staticmethod
    def as_dict(item):
        """Translate Alienvault MySQL query result to dict."""
        dict_ = {
            'name': item[0],
            'cidr': item[1],
        }

        return dict_

    def _conditions(self, name=None, cidr=None):
        conditions_dict = {
            name: "net.name = %s",
            cidr: "net.ips = %s",
        }

        keys = (name, cidr)

        query_conditions = [conditions_dict[key] for key in keys
                            if key is not None]
        condition_values = [key for key in keys if key is not None]

        return (" WHERE {}".format(" AND ".join(query_conditions)),
                condition_values)

    def __fields(self):
        query_fields = (
            "net.name AS name",
            "net.ips AS cidr",
        )

        return ", ".join(query_fields)

    def __columns(self):
        query_columns = (
            "net",
        )

        return ", ".join(query_columns)

    def __joins(self):
        return ""
