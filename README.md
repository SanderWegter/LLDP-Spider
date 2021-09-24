# LLDP-Spider

LLDP spider and mapper using snmp to poll devices for their LLDP neighbors and uses d3 to graph them.
This is based on Huawei equipment though it should work with other brands which support LLDP over SNMP as well.

[![LLDPMap](https://i.postimg.cc/Jh1WNCLG/lldpmap.png)](https://postimg.cc/Snt545jh)

## How to use

- Install the environment and libraries

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Edit the `config.yaml` file
- Run the spider

```bash
python spider.py
```

- Run the webserver

```bash
python serve.py
```

- Go to `http://localhost:8003`

## Changes

You can change the amount of groups based upon hostname. For my tests I had access to a network with 5 distinct groups

- isp-facing `ispXX.hostname.tld`
- customer-facing `custXX.hostname.tld`
- core `coreXX.hostname.tld`
- distribution `distXX.hostname.tld`
- access `accXX.hostname.tld`

To change the amount of groups (columns in the graph), change the configuration file. With 1 being the left-most column.

## TODO

- Add better switch icons, currently using placeholders
- Streamline the application
- More dynamic groups
- Port status
- Port labels
- Error handling
