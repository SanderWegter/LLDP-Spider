from easysnmp import Session
import yaml
import json

"""
 ||  ||
 \\()//
//(__)\\    Spider
||    ||

Sander Wegter 2021
"""


class Spider:
  def __init__(self, configuration):
    self.configuration = configuration
    self.used_switches = {}
    self.links = []
    self.nodes = []

    # https://support.huawei.com/enterprise/en/doc/EDOC1100065672/546de90a/lldp-mib
    self.walks = {
      "local_port": "1.0.8802.1.1.2.1.3.7.1.3",  # Local Port Name "XGigabitEthernet0/0/1"
      "local_desc": "1.0.8802.1.1.2.1.3.7.1.4",  # Local Port Desc "XG0/0/1 to FN1 GE1/0/16"
      "remote_port": "1.0.8802.1.1.2.1.4.1.1.7",  # Remote Port Name "GigabitEthernet1/0/16"
      "remote_desc": "1.0.8802.1.1.2.1.4.1.1.8",  # Remote Port Desc "GE1/0/16 LAG Trunk1 to Core1a XG0/0/1 Trunk 5
      "remote_host": "1.0.8802.1.1.2.1.4.1.1.9",  # Remote hostname "fn1-s00.mgmt.f1dev"
      "remote_ver": "1.0.8802.1.1.2.1.4.1.1.10",  # Remote device Desc "Huawei Versatile Routing P etc"
    }

    self.groups = configuration["host_groups"]

  def walk(self, host, oid):
    if self.configuration["host_should_contain"] not in host:
      return []
    s = Session(hostname=host, version=2, community=self.configuration["snmp_community"])
    return s.walk(oid)

  def get(self, host, oid):
    if self.configuration["host_should_contain"] not in host:
      return []
    s = Session(hostname=host, version=2, community=self.configuration["snmp_community"])
    return s.get(oid)

  def discover_network(self, cur_host):
    if cur_host not in self.used_switches:
      print(f"Doing {cur_host}")
      self.used_switches[cur_host] = []
      remote_hosts = self.walk(cur_host, self.walks["remote_host"])

      for host in remote_hosts:
        port_oid_label = ".".join(host.oid.split(".")[-3:])
        local_port_oid = port_oid_label.split(".")[1]
        local_port_name = self.get(cur_host, f"{self.walks['local_port']}.{local_port_oid}").value
        remote_port_name = self.get(cur_host, f"{self.walks['remote_port']}.{port_oid_label}").value

        self.links.append(
          {
            "a": [cur_host, local_port_name],
            "z": [host.value, remote_port_name],
            "value": "10",
            "color": "black",
          }
        )
        if self.configuration["host_should_contain"] not in host.value:
          self.links.append(
            {
              "a": [host.value, remote_port_name],
              "z": [cur_host, local_port_name],
              "value": "10",
              "color": "black",
            }
          )

      node_group = "1"
      for group in self.groups:
        if group in cur_host.split(".")[0] and self.configuration["host_should_contain"] in cur_host:
          node_group = self.groups[group]
          break
      self.nodes.append(
        {"label": cur_host, "size": 32, "group": str(node_group), "information": {"hostname": cur_host}}
      )

      sub_hosts = self.walk(cur_host, self.walks["remote_host"])
      for next_host in sub_hosts:
        self.discover_network(next_host.value)
    return {"nodes": self.nodes, "links": self.links}

  def crawl_network(self):
    first_host = self.configuration["first_host"]
    network = self.discover_network(first_host)
    return network


if __name__ == "__main__":
  config = yaml.safe_load(open("config.yaml"))
  spider = Spider(config)
  network = spider.crawl_network()
  with open("output.json", "w") as f:
    f.write(json.dumps(network))
