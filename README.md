### dynamic-k8s

- Dynamic Inventory Create
- Kubespray in Containerd

### Prerequisites

- Kubernetes 1.19+
- python 3.x+

### Setup and Installation

#### INIT

- Install
  - pip3
    - package
  - nerdctl v1.0.0
  - cni-plugins v1.1.1

```
./init
```

### How-to

```
python3 dynamic.py --help

usage: dynamic.py [-h] [-c COUNT] [-u USERNAME] [-p PASSWORD] [-P PORT] [-ip [IPADDRESS [IPADDRESS ...]]] [--reset RESET]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Number of Control Plane. (Default. 1)
  -u USERNAME, --username USERNAME
                        ssh connection ID.
  -p PASSWORD, --password PASSWORD
                        ssh connection Password.
  -P PORT, --port PORT  ssh connection Port.
  -ip [IPADDRESS [IPADDRESS ...]], --ipaddress [IPADDRESS [IPADDRESS ...]]
                        ip address ex) 10.0.0.1 10.0.0.2 10.0.0.3")
  --reset RESET         reset

example) python3 dynamic.py -c 1 -u username -p password -P 22 -ip 10.0.0.1 10.0.0.2 10.0.0.3
```
