import json
from multiprocessing.dummy import Pool as ThreadPool
from flask import Blueprint, abort
from .import app, db_mysql
from .models import HostPorts, Hosts, ScanResults
from sqlalchemy import select, insert
import xml.etree.ElementTree as ET
import ipaddress 
import os
import subprocess
import threading
import datetime
import numpy


procs = Blueprint('procs', __name__)


@procs.route('/start', methods=['GET'])
def start():
    nmap_bin = os.getenv('NMAP')
    if not os.path.isfile(nmap_bin):
        app.logger.info(f"nmap binary not found {nmap_bin}")
        abort(500, f"nmap binary not found {nmap_bin}")

    get_hosts_qry = select(Hosts.ip, Hosts.id)
    hosts = db_mysql.session.execute(get_hosts_qry)

    addresses = []
    for item in hosts:
        # insert_ports(item.ip, 80)
        host_str = int(item.ip.decode())
        addr = str(ipaddress.ip_address(host_str))
        addresses.append(addr)
    
    db_mysql.session.close()

    nmap_thread = threading.Thread(target=start_pool, args=(addresses,))
    nmap_thread.start()

    return "OK", 200


def start_pool(addresses):
    parallel_jobs = int(os.getenv('PARALLEL_JOBS'))
    pool = ThreadPool(processes=parallel_jobs)
    pool.map(scan_host, addresses)
    pool.close()


@procs.route('/scan_host/<string:ip_addr>', methods=['GET'])
def scan_host(ip_addr):
    app.logger.info(f"INFO start scannig {ip_addr}")
    ip_string = int(ipaddress.ip_address(ip_addr))
    check_ip_qry = select(Hosts).where(Hosts.ip==ip_string)
    check_ip = db_mysql.session.execute(check_ip_qry).scalar()
    db_mysql.session.close()
    if check_ip is None:
        msg = f"ERROR ip {ip_addr} not found in hosts table"
        app.logger.info(msg)
        abort(404, msg)
    # p = subprocess.Popen(["nmap", "-oX", "-", addr, "-p", "0-65535", "-sV"], stdout=subprocess.PIPE)
    p = subprocess.Popen(["nmap", "-oX", "-", ip_addr, "-sV"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    if err is not None:
        app.logger.info(f"ERROR subprocess {err}")

    root = ET.fromstring(output.decode())
    
    for elem in root.findall("./host/ports/port"):
        port = elem.attrib['portid']
        insert_ports(ip_addr, int(port))

    app.logger.info(f"INFO finish scannig {ip_addr}")
    return "OK", 200


@procs.route('/check_host/<string:ip_addr>', methods=['GET'])
def check_host(ip_addr):
    app.logger.info(f"INFO check_host {ip_addr}")
    ip_string = int(ipaddress.ip_address(ip_addr))
    check_time_qry = select(ScanResults.host_id, ScanResults.scantime).filter(Hosts.id==ScanResults.host_id, Hosts.ip==ip_string).order_by(ScanResults.scantime.desc()).limit(1)
    check_time = db_mysql.session.execute(check_time_qry).one()
    if check_time is None:
        msg = f"ERROR ip {ip_addr} not found in hosts table"
        app.logger.info(msg)
        abort(404, msg)

    ten_seconds = datetime.timedelta(seconds=10)
    select_time = check_time[1] - ten_seconds
    host_id = check_time[0]

    get_ports_open_qry = select(ScanResults.port).where(ScanResults.scantime>select_time, ScanResults.host_id==host_id)
    get_ports_open = db_mysql.session.execute(get_ports_open_qry)
    ports_open = numpy.array([int(i[0]) for i in get_ports_open])

    get_ports_qry = select(HostPorts.port).where(HostPorts.host_id==host_id)
    get_ports = db_mysql.session.execute(get_ports_qry)
    ports_fixed = numpy.array([int(i[0]) for i in get_ports])
    
    db_mysql.session.close()

    if numpy.array_equal(ports_open,ports_fixed):
        return {"status": True, "open_miss": None, "open_add": None}
    else:
        class NumpyArrayEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, numpy.ndarray):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)

        diff1 = numpy.setdiff1d(ports_fixed,ports_open)
        diff2 = numpy.setdiff1d(ports_open,ports_fixed)

        encoded_diff1 = json.dumps(diff1, cls=NumpyArrayEncoder)
        encoded_diff2 = json.dumps(diff2, cls=NumpyArrayEncoder)

        return {"status": False, "open_miss": encoded_diff1, "open_add": encoded_diff2}


def insert_ports(host, port):
    with app.app_context():
        ip_string = int(ipaddress.ip_address(host))
        get_host_id = select(Hosts.id).where(Hosts.ip==ip_string)
        host_id = db_mysql.session.execute(get_host_id).scalar()
        insert_port = db_mysql.insert(ScanResults).values(host_id=int(host_id), port=int(port), id=None, scantime=None, status=None)
        db_mysql.session.execute(insert_port)
        db_mysql.session.commit()
        db_mysql.session.close()
