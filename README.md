ossimdb-to-json allows you to fetch information from OSSIM (Alienvault) as a
python dictionary format.

Creating an Alienvault object, you can access to the following models:

- Hosts
- Interfaces
- MAC Vendors
- Host Properties
- Host Services
- Networks

INSTALL
-------

```
apt-get install libmysqlclient-dev
python setup.py install
```

CONFIGURATION
-------------

First of all, you need to perform some extra configurations on your Alienvault:

- Bind your MySQL address to the desired interface (0.0.0.0 by default).
  Maybe you prefer to restrict this to your local network.

- Add this rule on the firewall BEFORE the reject one:

```
# First get the iptables list with the line numbers enabled
$ iptables -nL --line-numbers

# Look up the REJECT rule line number and replace {LINE_NUMBER} with it
$ iptables -I INPUT {LINE_NUMBER} -i eth1 -p tcp --dport 3306 -s {SOURCE_IP} -j ACCEPT
```

- Create a read-only user for your app:

```
CREATE USER 'user'@'%' IDENTIFIED BY 'password';
GRANT SELECT ON alienvault.* TO 'user'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

EXAMPLE
-------

Just apply the filters you want to the object and call the result() method.

```
from ossimdb_to_json import Alienvault

av_orm = Alienvault()

av_orm.connect('192.168.1.20s', 'user', 'password')

av_orm.hosts.all().result()
av_orm.hosts.filter(ip='192.168.1.1').result()
```
