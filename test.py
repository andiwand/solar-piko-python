import http.client
import html.parser
import base64
import time
import sqlite3


HOST = "192.168.15.11"
PORT = 80
AUTH = b"pvserver:stefl"

DB_PATH = "test.db"
DB_INIT_PATH = "init.sql"
DB_INIT = None
with open(DB_INIT_PATH, "r") as f:
    DB_INIT = f.read()

METADATA = {(2, 3, 2): "power",
            (2, 7, 2): "status",
            (2, 3, 5): "total",
            (2, 5, 5): "day",
            (2, 13, 2): "input1_voltage",
            (2, 15, 2): "input1_current",
            (2, 18, 2): "input2_voltage",
            (2, 20, 2): "input2_current",
            (2, 13, 5): "output1_voltage",
            (2, 15, 5): "output1_power",
            (2, 18, 5): "output2_voltage",
            (2, 20, 5): "output2_power",
            (2, 23, 5): "output3_voltage",
            (2, 25, 5): "output3_power"}

last_data = None


class HTMLParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        html.parser.HTMLParser.__init__(self, *args, **kwargs)
        self.path = []
        self.table_depth = 0
        self.position = [0, 0, 0]
    
    def handle_starttag(self, tag, attrs):
        self.path.append(tag)
        attrs = dict(attrs)
        
        if tag == "table":
            self.table_depth += 1
            return
        
        if self.table_depth == 1:
            if tag in ("tr", "th"):
                self.rowspan = int(attrs.get("rowspan", 1))
            elif tag == "td":
                self.colspan = int(attrs.get("colspan", 1))
    
    def handle_endtag(self, tag):
        self.path.pop()
        
        if self.table_depth == 1:
            if tag == "table":
                self.position[0] += 1
                self.position[1] = 0
            elif tag in ("tr", "th"):
                self.position[1] += self.rowspan
                self.position[2] = 0
            elif tag == "td":
                self.position[2] += self.colspan
        
        if tag == "table": self.table_depth -= 1
    
    def handle_data(self, data):
        if not self.path or self.path[-1] != "td": return
        if self.table_depth > 1: return
        
        data = bytes(data, "utf-8").decode("unicode_escape").strip()
        if data == "x x x": data = "0"
        name = METADATA.get(tuple(self.position))
        if name: last_data[name] = data


c = http.client.HTTPConnection(HOST, PORT)
auth = base64.b64encode(AUTH).decode("ascii")

db_init = True
con = sqlite3.connect(DB_PATH)
cur = con.cursor()
if db_init: cur.executescript(DB_INIT)

while True:
    c.request("GET", "/", headers={"Authorization": "Basic " + auth})
    r = c.getresponse()
    
    last_data = {}
    timestamp = int(round(time.time() * 1000))
    parser = HTMLParser()
    parser.feed(str(r.read()))
    
    cur.execute("INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (timestamp, last_data["status"], last_data["power"],
                 last_data["input1_voltage"], last_data["input1_current"],
                 last_data["input2_voltage"], last_data["input2_current"],
                 last_data["output1_voltage"], last_data["output1_power"],
                 last_data["output1_voltage"], last_data["output1_power"],
                 last_data["output1_voltage"], last_data["output1_power"],
                 last_data["day"], last_data["total"]))
    con.commit()
    
    time.sleep(0)

con.commit()
con.close()