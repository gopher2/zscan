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
                "hostname"	TEXT,
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
    
    c.execute('''CREATE TABLE "Port" (
                "port_number"	    INTEGER NOT NULL UNIQUE,
                "port_description"	TEXT,
                "scan_enabled"	    INTEGER,
                PRIMARY KEY("port_number")
            )''')
    
    c.execute('''CREATE TABLE "NetworkPorts" (
                "network_id"	            INTEGER,
                "port_id"	                INTEGER,
                FOREIGN KEY("port_id")      REFERENCES "Port"("port_number"),
                FOREIGN KEY("network_id")   REFERENCES "Networks"("network_id")
            )''')

    networks = [("192.168.88.0/24", 1, "Mikrotik Default" ),
                ("169.254.0.0/16",  0, "APIPA"            ),
                ("192.168.10.0/24", 0, "Common Home LAN"  )]
    
    c.executemany('INSERT INTO Networks (cidr, enabled, description) VALUES(?,?,?)', networks)

    ports = [   (21,  0,"ftp"),
                (22,  0,"ssh"),
                (23,  0,"telnet"),
                (25,  0,"smtp"),
                (53,  0,"domain"),
                (80,  1,"http"),
                (110, 0,"pop3"),
                (111, 0,"rpcbind"),
                (135, 0,"msrpc"),
                (139, 0,"netbios-ssn"),
                (143, 0,"imap"),
                (443, 1,"https"),
                (445, 0,"microsoft-ds"),
                (993, 0,"imaps"),
                (995, 0,"pop3s"),
                (1723,0,"pptp"),
                (3306,0,"mysql"),
                (3389,0,"ms-wbt-server"),
                (5900,0,"vnc"),
                (8080,0,"http-proxy")]

    c.executemany('INSERT INTO Port (port_number, scan_enabled, port_description) VALUES(?,?,?)', ports)
    conn.commit()
    
    ### Poupulate the networks port to scan from the global list
    c.execute('''   INSERT INTO NetworkPorts (network_id, port_id) 
                        SELECT
						    Networks.network_id, 
						    Port.port_number
					    FROM
						    Networks
						    CROSS JOIN Port
                        WHERE
    						Networks.enabled = 1
	    					AND Port.scan_enabled = 1 ''')
    conn.commit()
    conn.close()