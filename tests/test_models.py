from __future__ import absolute_import

import unittest

from ossimdb_to_json import Alienvault

AV = None

# Configure your testing database here.
HOST = 'X.X.X.X'
USER = 'user'
PWD = 'password'
DB = 'alienvault'


def setUpModule():
    global AV
    AV = Alienvault()
    AV.connect(HOST, USER, PWD, DB)


def tearDownModule():
    global AV
    AV.close()


class HostManagerTest(unittest.TestCase):
    """Test HostManager."""

    def test_fetch_all(self):
        """Test we can fetch hosts from database."""
        av_hosts = AV.hosts.all().result()
        self.assertNotEqual(len(av_hosts), 0)

    def test_filter(self):
        """Test we can filter hosts."""
        av_hosts = AV.hosts.filter(ip=HOST).result()
        self.assertNotEqual(len(av_hosts), 0)


class InterfaceManagerTest(unittest.TestCase):
    """Test InterfaceManager."""

    def test_fetch_all(self):
        """Test we can fetch interfaces from database."""
        av_interfaces = AV.interfaces.all().result()
        self.assertNotEqual(len(av_interfaces), 0)

    def test_filter(self):
        """Test we can filter interfaces."""
        av_interfaces = AV.interfaces.filter(ip=HOST).result()
        self.assertNotEqual(len(av_interfaces), 0)


class MacVendorManagerTest(unittest.TestCase):
    """Test MacVendorManager."""

    def test_fetch_all(self):
        """Test we can fetch MAC vendors from database."""
        av_mac_vendors = AV.mac_vendors.all().result()
        self.assertNotEqual(len(av_mac_vendors), 0)

    def test_filter(self):
        """Test we can filter MAC vendors."""
        av_interfaces = AV.interfaces.filter(ip=HOST).result()
        self.assertNotEqual(len(av_interfaces), 0)


class HostPropertyManagerTest(unittest.TestCase):
    """Test HostPropertyManager."""

    def test_fetch_all(self):
        """Test we can fetch host properties from database."""
        av_host_properties = AV.host_properties.all().result()
        self.assertNotEqual(len(av_host_properties), 0)

    def test_filter(self):
        """Test we can filter host properties."""
        av_host_properties = AV.host_properties.filter(name='cpu').result()
        self.assertNotEqual(len(av_host_properties), 0)


class HostServiceManagerTest(unittest.TestCase):
    """Test HostServiceManager."""

    def test_fetch_all(self):
        """Test we can fetch host services from database."""
        av_host_services = AV.host_services.all().result()
        self.assertNotEqual(len(av_host_services), 0)

    def test_filter(self):
        """Test we can filter host services."""
        av_host_services = AV.host_services.filter(ip=HOST).result()
        self.assertNotEqual(len(av_host_services), 0)


class NetworkManagerTest(unittest.TestCase):
    """Test NetworkManager."""

    def test_fetch_all(self):
        """Test we can fetch networks from database."""
        av_networks = AV.networks.all().result()
        self.assertNotEqual(len(av_networks), 0)

    def test_filter(self):
        """Test we can filter networks."""
        av_networks = AV.networks.filter(cidr='0.0.0.0/32').result()
        self.assertNotEqual(len(av_networks), 0)

if __name__ == '__main__':
    unittest.main()
