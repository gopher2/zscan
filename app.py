from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/hosts/<host_id>')
def host_listing(host_id):
        host_data = query_single_host_data(host_id)
        return render_template('hostdetail.html', host_data=host_data)


@app.route('/hosts')
def all_host_listing():
        host_data = query_all_host_data()
        return render_template('hosts.html', host_data=host_data)



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
                    OpenPorts.host_id = ? '''
    
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