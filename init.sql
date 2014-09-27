DROP TABLE IF EXISTS data;

CREATE TABLE data (date INTEGER PRIMARY KEY, status TEXT, power INTEGER,
                   input1_voltage INTEGER, input1_current REAL,
                   input2_voltage INTEGER, input2_current REAL,
                   output1_voltage INTEGER, output1_power INTEGER,
                   output2_voltage INTEGER, output2_power INTEGER,
                   output3_voltage INTEGER, output3_power INTEGER,
                   day REAL, total INTEGER);