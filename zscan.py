#!/usr/bin/env python
#IMPORT THE MODULES NECCESSARY TO RUN PROGRAM
import sqlite3
import configparser
import sqlite3 as sl
import sys
import ipaddress
import os
import time


def create_connection(db_file):                        
    # CREATES THE CONNETION TO THE SQLITE DATABASE 
    conn = None
    try:
        conn = sl.connect(db_file)
    except Error as e:
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

def update_host(conn, IP_Address, scan_id, port):       
    # IF OPEN PORT FOUND ADD HOST, UPDATE LAST SCAN TIME IF ALREADY SEEN
    sql = ''' INSERT INTO Hosts(IP_Address,last_scan_id) VALUES(?,?) ON CONFLICT(IP_Address) DO UPDATE SET last_scan_id = ? '''
    cur = conn.cursor()
    values = (IP_Address, scan_id, scan_id)
    cur.execute(sql, values)
    
    # GET THE CURRENT HOST ID
    cur = conn.cursor()
    sql = ''' SELECT host_id FROM Hosts where IP_Address = ? '''
    cur.execute(sql, (IP_Address,))
    host_id = cur.fetchone()[0]
    
    # ADD THE PORT TO THE SCAN RESULTS
    sql = ''' INSERT INTO Ports(host_id, scan_id, number) VALUES(?,?,?) '''
    cur = conn.cursor()
    values = (host_id, scan_id, port)
    cur.execute(sql, values)
    conn.commit()
    
sqlite3.enable_callback_tracebacks(True)
def main():
    sqlite3.enable_callback_tracebacks(True)
    config = configparser.ConfigParser()
    config.sections()
    config.read('zscan.cfg')   
    ports = [int(x) for x in config.get('zscan', 'ports').split(',')]
    networks = config.get('zscan', 'networks').split(',')
    zmap = config.get('zscan', 'zmaplocation')
    dbfile = config.get('zscan', 'dbfile')
    conn = create_connection(dbfile)

    with conn:
        for network in networks:
            for port in ports:
                print ("SCANNING NETWORK: " + str(network) + " PORT: " + str(port))
                command = zmap + " -v 0 -q -r 300 -p " + str(port).rstrip() + " " + network
                scan = (int(time.time()), command)
                scan_id = create_scan(conn, scan)
                with os.popen(command) as pipe:
                    for output in pipe:
                        IP_Address = output.rstrip()
                        print ("HOST: " + IP_Address + " OPEN PORT: " + str(port))
                        update_host(conn, IP_Address, scan_id, port)
                scan = (int(time.time()), scan_id)
                end_scan(conn, scan)

if __name__ == '__main__':
    main()




