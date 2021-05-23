#!/usr/bin/env python

import os
import configparser
import sqlite3 as sl

def resetdb():
    print("EREASING ALL SQLITE DATA AND PRELOADING WITH DEFAULT VALUES")

    config = configparser.ConfigParser()
    config.sections()
    config.read('zscan.cfg')   
    dbfile = config.get('zscan', 'dbfile')

    if os.path.exists(dbfile):
        os.remove(dbfile) 

    conn = sl.connect(dbfile)  
    c = conn.cursor() 

    c.execute('''CREATE TABLE "Scans" (
                "scan_id"	    INTEGER NOT NULL UNIQUE,
                "starttime"	    INTEGER,
                "endtime"	    INTEGER,
                "arguments"	    TEXT,
                PRIMARY KEY("scan_id" AUTOINCREMENT)
            )''')

    c.execute('''CREATE TABLE "Hosts" (
                "host_id"	    INTEGER,
                "network_id"	INTEGER,
                "last_scan_id"	INTEGER,
                "IP_Address"	TEXT NOT NULL UNIQUE,
                "name"	TEXT,
                FOREIGN KEY("last_scan_id") REFERENCES "Scans"("scan_id"),
                PRIMARY KEY("host_id" AUTOINCREMENT)
            )''')

    c.execute('''CREATE TABLE "OpenPorts" (
                "port_id"	    INTEGER NOT NULL UNIQUE,
                "host_id"	    INTEGER,
                "scan_id"	    INTEGER,
                "number"	    INTEGER NOT NULL,
                PRIMARY KEY("port_id" AUTOINCREMENT),
                FOREIGN KEY("host_id") REFERENCES "Hosts"("host_id")
                )''')

    c.execute('''CREATE TABLE "Networks" (
                "network_id"	INTEGER NOT NULL UNIQUE,
                "cidr"	        TEXT UNIQUE,
                "enabled"	    INTEGER,
                "description"	TEXT,
                PRIMARY KEY("network_id" AUTOINCREMENT)
            )''')
    
    c.execute('''CREATE TABLE "PortList" (
                "port_number"	    INTEGER NOT NULL UNIQUE,
                "port_description"	TEXT,
                "scan_enabled"	    INTEGER,
                PRIMARY KEY("port_number")
            )''')

    networks = [("192.168.88.0/24", 1, "Mikrotik Default" ),
                ("169.254.0.0/16",  0, "APIPA"            ),
                ("192.168.10.0/24", 0, "Common Home LAN"  )]
    
    c.executemany('INSERT INTO Networks (cidr, enabled, description) VALUES(?,?,?)', networks)

    ports = [   (21,  1,"ftp"),
                (22,  1,"ssh"),
                (23,  1,"telnet"),
                (25,  1,"smtp"),
                (53,  1,"domain"),
                (80,  1,"http"),
                (110, 1,"pop3"),
                (111, 1,"rpcbind"),
                (135, 1,"msrpc"),
                (139, 1,"netbios-ssn"),
                (143, 1,"imap"),
                (443, 1,"https"),
                (445, 1,"microsoft-ds"),
                (993, 1,"imaps"),
                (995, 1,"pop3s"),
                (1723,1,"pptp"),
                (3306,1,"mysql"),
                (3389,1,"ms-wbt-server"),
                (5900,1,"vnc"),
                (8080,1,"http-proxy")]

    c.executemany('INSERT INTO PortList (port_number, scan_enabled, port_description) VALUES(?,?,?)', ports)
    conn.commit()
    conn.close()