#!/usr/bin/env python
import sqlite3
from sqlite3 import Error
import configparser
import sqlite3 as sl
import sys
import ipaddress
import os
import time

def create_connection(db_file):
    conn = None
    try:
        print ("Trying to connect to "+ db_file)
        conn = sl.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_scan(conn, values):
    sql = ''' INSERT INTO Scans(starttime,arguments) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    return cur.lastrowid

def end_scan(conn, values):
    sql = ''' Update Scans SET endtime  = ? WHERE scan_id = ? '''
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()

def update_host(conn, IP_Address, scan_id, port):
    sql = ''' INSERT OR REPLACE INTO Hosts(IP_Address,scan_id) VALUES(?,?) '''
    cur = conn.cursor()
    values = (IP_Address, scan_id)
    cur.execute(sql, values)
    host_id = cur.lastrowid
    sql = ''' INSERT INTO Ports(host_id, number) VALUES(?,?) '''
    cur = conn.cursor()
    values = (host_id, port)
    cur.execute(sql, values)
    conn.commit()
    

def main():
    config = configparser.ConfigParser()
    config.sections()
    config.read('zscan.cfg')   
    ports = [int(x) for x in config.get('zscan', 'ports').split(',')]
    networks = config.get('zscan', 'networks').split(',')
    zmap = config.get('zscan', 'zmaplocation')
    dbfile = config.get('zscan', 'dbfile')
    print (dbfile)
    conn = create_connection(dbfile)

    with conn:
        for network in networks:
            for port in ports:
                command = zmap + " -q -p " + str(port).rstrip() + " " + network
                print ("RUNNING COMMAND: " + command)
                scan = (int(time.time()), command)
                scan_id = create_scan(conn, scan)
                with os.popen(command) as pipe:
                    for IP_Address in pipe:
                        print ("SCAN: " + str(scan_id) + " HOST: " + IP_Address.rstrip() + " HAS PORT " + str(port) + " OPEN")
                        #update_host(conn, IP_Address, scan_id, port)
                scan = (int(time.time()), scan_id)
                end_scan(conn, scan)

if __name__ == '__main__':
    main()




