from . import db_mysql


class Hosts(db_mysql.Model):
    __tablename__ = 'hosts'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    ip = db_mysql.Column(db_mysql.VARBINARY(16))


class HostPorts(db_mysql.Model):
    __tablename__ = 'host_ports'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    port = db_mysql.Column(db_mysql.Integer)
    host_id = db_mysql.Column(db_mysql.Integer)


class HPBridge(db_mysql.Model):
    __tablename__ = 'scan_result'
    id = db_mysql.Column(db_mysql.Integer, primary_key=True, autoincrement=True)
    host_id = db_mysql.Column(db_mysql.Integer)
    port = db_mysql.Column(db_mysql.Integer)
    status = db_mysql.Column(db_mysql.VARCHAR(255))
    scantime = db_mysql.Column(db_mysql.DateTime)
