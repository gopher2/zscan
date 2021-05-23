#!/usr/bin/env python
#IMPORT THE MODULES NECCESSARY TO RUN PROGRAM
import sqlite3
import configparser
import sqlite3 as sl
import os
import time


def create_connection(db_file):                        
    # CREATES THE CONNETION TO THE SQLITE DATABASE 
    conn = None
    try:
        conn = sl.connect(db_file)
    except configparser.Error as e:
        print(e)
    return conn

def create_scan(conn, values):                          
    # INSERT A NEW NETWORK SCAN EVENT TO THE DATABASE
    sql = ''' INSERT INTO Scans(starttime,arguments) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.lastrowid

def end_scan(conn, values):                             
    # MARK THE ENDING TIMESTAMP OF A NETWORK SCAN
    sql = ''' Update Scans SET endtime  = ? WHERE scan_id = ? '''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()

def update_host(conn, IP_Address, scan_id, port, network_id):       
    # IF OPEN PORT FOUND ADD HOST, UPDATE LAST SCAN TIME IF ALREADY SEEN
    sql = ''' INSERT INTO Hosts(network_id, IP_Address,last_scan_id) VALUES(?,?,?) ON CONFLICT(IP_Address) DO UPDATE SET last_scan_id = ? '''
    cur = conn.cursor()
    values = (network_id, IP_Address, scan_id, scan_id)
    cur.execute(sql, values)
    
    # GET THE CURRENT HOST ID
    cur = conn.cursor()
    sql = ''' SELECT host_id FROM Hosts where IP_Address = ? '''
    cur.execute(sql, (IP_Address,))
    host_id = cur.fetchone()[0]
    
    # ADD THE PORT TO THE SCAN RESULTS
    sql = ''' INSERT INTO OpenPorts(host_id, scan_id, number) VALUES(?,?,?) '''
    cur = conn.cursor()
    values = (host_id, scan_id, port)
    cur.execute(sql, values)
    conn.commit()

def get_enabled_networks(conn):
    # GET LIST OF NETWORKS FLAGGED FOR SCANNING
    cur = conn.cursor()
    cur.execute(''' SELECT network_id, cidr FROM Networks where enabled = 1 ''')
    return cur.fetchall()

def get_enabled_ports(conn):
    # GET LIST OF PORTS TO SCAN (MAKE NETWORK DEPENDANT?)
    cur = conn.cursor()
    cur.execute(''' SELECT port_number, port_description FROM PortList where scan_enabled = 1 ''')
    return cur.fetchall()

# def initalize_database:
#     #WIPE OUT AND INITALIZE DATABASE WITH DEFAULT VALUES


sqlite3.enable_callback_tracebacks(True)
def main():
    sqlite3.enable_callback_tracebacks(True)
    config = configparser.ConfigParser()
    config.sections()
    config.read('zscan.cfg')   
    zmap = config.get('zscan', 'zmaplocation')
    dbfile = config.get('zscan', 'dbfile')
    conn = create_connection(dbfile)

    with conn:
        networks = get_enabled_networks(conn)
        for network in networks:
            network_id, cidr = network
            ports = get_enabled_ports(conn)
            for port in ports:
                port_number, port_name = port
                command = zmap + " -v 0 -q -r 300 -p " + str(port_number) + " " + cidr
                scan = (int(time.time()), command)
                scan_id = create_scan(conn, scan)
                with os.popen(command) as pipe:
                    for output in pipe:
                        IP_Address = output.rstrip()
                        print ('HOST:{:16s}OPEN PORT:{:s}/{:d}'.format(IP_Address,port_name,port_number))
                        update_host(conn, IP_Address, scan_id, port_number, network_id)
                scan = (int(time.time()), scan_id)
                end_scan(conn, scan)

if __name__ == '__main__':
    main()