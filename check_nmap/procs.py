from multiprocessing.dummy import Pool as ThreadPool
from flask import Blueprint, abort
from .import app, db_mysql
from .models import HostPorts, Hosts
import xml.etree.ElementTree as ET
import ipaddress 
import os
import subprocess
import threading


procs = Blueprint('procs', __name__)


@procs.route('/start', methods=['GET'])
def start():
    nmap_bin = os.getenv('NMAP')
    if not os.path.isfile(nmap_bin):
        app.logger.info(f"nmap binary not found {nmap_bin}")
        abort(500, f"nmap binary not found {nmap_bin}")

    sess_get_hosts = db_mysql
    get_hosts_qry = sess_get_hosts.select(Hosts.ip, Hosts.id)
    hosts = sess_get_hosts.session.execute(get_hosts_qry)

    addresses = []
    for item in hosts:
        host_str = int(item.ip.decode())
        addr = str(ipaddress.ip_address(host_str))
        addresses.append(addr)

    sess_get_hosts.session.close()

    nmap_thread = threading.Thread(target=start_pool, args=(addresses,))
    nmap_thread.start()

    return "OK", 200


def start_pool(addresses):
    parallel_jobs = int(os.getenv('PARALLEL_JOBS'))
    pool = ThreadPool(processes=parallel_jobs)
    pool.map(scan_host, addresses)
    pool.close()


def scan_host(ip_addr):
    app.logger.info(f"INFO start scannig {ip_addr}")
    # p = subprocess.Popen(["nmap", "-oX", "-", addr, "-p", "0-65535", "-sV"], stdout=subprocess.PIPE)
    p = subprocess.Popen(["nmap", "-oX", "-", ip_addr, "-sV"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    if err is not None:
        app.logger.info(f"ERROR subprocess {err}")

    root = ET.fromstring(output.decode())
    
    ports = []
    for elem in root.findall("./host/ports/port"):
        
        ports.append(elem.attrib['portid'])

    app.logger.info(f"INFO finish scannig {ip_addr}")
    print(ip_addr, ports)
    return ports