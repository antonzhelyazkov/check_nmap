from . import db_mysql


class HostsIPV4(db_mysql.Model):
    __tablename__ = 'hosts_ipv4'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    ip = db_mysql.Column(db_mysql.Integer)


class HostPortsIPV4(db_mysql.Model):
    __tablename__ = 'host_ports_ipv4'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    port = db_mysql.Column(db_mysql.Integer)
    host_id = db_mysql.Column(db_mysql.Integer)


class ScanResults(db_mysql.Model):
    __tablename__ = 'scan_result'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    host_id = db_mysql.Column(db_mysql.Integer)
    port = db_mysql.Column(db_mysql.Integer)
    status = db_mysql.Column(db_mysql.VARCHAR(255))
    scantime = db_mysql.Column(db_mysql.DateTime)
