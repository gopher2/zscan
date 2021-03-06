from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def view_home():
    return render_template("base.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(504)
def page_not_found(e):
    return render_template("500.html")

@app.route('/hosts')
def all_host_listing():
        host_data = query_all_host_data()
        return render_template('hosts.html', title="Zscan Home", host_data=host_data)

@app.route('/hosts/<host_id>')
def host_listing(host_id):
        host_data = query_single_host_data(host_id)
        host_info = query_host_info(host_id)
        return render_template('hostdetail.html', host_data=host_data, host_info=host_info)

@app.route('/networks')
def network_listing():
        network_data = query_all_networks()
        return render_template('networks.html', network_data=network_data)

@app.route('/networks/<network_id>')
def network_detail(network_id):
        network_data = query_network(network_id)
        network_info = query_network_info(network_id)
        return render_template('networkdetail.html', network_data=network_data, network_info=network_info)

@app.route('/ports')
def port_listing():
        port_data = query_all_ports()
        return render_template('ports.html', port_data=port_data)

def query_all_ports():
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT
                    port_number,
                    port_description,
                    scan_enabled
                FROM
                    Port
                '''   
    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    return rows

def query_network_info(network_id):

    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT
                    description, cidr
                FROM 
                    Networks
                WHERE
                    network_id = ? '''
    c = conn.cursor()
    c.execute(sql, (network_id,))
    row = c.fetchone()
    return row

def query_host_info(host_id):
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT
                    IP_Address, hostname
                FROM 
                    Hosts
                WHERE
                    host_id = ? '''
    c = conn.cursor()
    c.execute(sql, (host_id,))
    row = c.fetchone()
    return row

def query_network(network_id):
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT 
                    port_number,
                    CASE 
                        WHEN EXISTS (SELECT * from NetworkPorts where network_id = ? and port_id = port_number)
                        THEN 'TRUE'
                        ELSE 'FLASE'
                    END enabled
                FROM	
                    Port '''

    c = conn.cursor()
    c.execute(sql, (network_id,))
    rows = c.fetchall()
    return rows

def query_all_networks():
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT
                    network_id,
                    cidr as network,
                    description,
                    enabled
                FROM
                    Networks
                '''   
    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    return rows

def query_single_host_data(host_id):
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row
    sql = '''   SELECT
                    Hosts.IP_Address as ip_address,
                    Port.port_description as service,
                    number as port,
                    datetime(starttime, 'unixepoch', 'localtime') AS scantime
                FROM
                    OpenPorts 
                    INNER JOIN Port     ON OpenPorts.number  = Port.port_number
                    INNER JOIN Hosts    ON OpenPorts.host_id = Hosts.host_id
                    INNER JOIN Scans    ON OpenPorts.scan_id = Scans.scan_id
                WHERE
                    OpenPorts.host_id = ? 
                GROUP BY
                    port '''
    
    c = conn.cursor()
    c.execute(sql, (host_id,))
    rows = c.fetchall()
    return rows

def query_all_host_data():
    conn = sqlite3.connect("zscan.db")
    conn.row_factory = sqlite3.Row

    sql = '''   SELECT 
                    Hosts.host_id,
                    Networks.description as network,
                    IP_Address, 
                    Hostname, 
                    datetime(starttime, 'unixepoch', 'localtime') AS starttime, 
                    count(OpenPorts.port_id) as openports
                FROM 
                    Hosts 
                    INNER JOIN Networks ON Hosts.network_id =   Networks.network_id
                    INNER JOIN scans    ON Hosts.last_scan_id = Scans.scan_id 
                    LEFT JOIN OpenPorts ON OpenPorts.host_id =  Hosts.host_id 
                GROUP BY
                    Hosts.host_id 
                ORDER BY
                    Networks.network_id,
                    Hosts.IP_Address '''

    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    return rows

if __name__ == '__main__':
    app.run()