#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:35:20 2020

@author: aurelien
"""

import numpy as np
import pandas as pd

import sqlite3
import csv
import matplotlib.pyplot as plt

plt.close("all")

def export_journals(tnames):
    tnames_sorted = sorted(tnames)
    with open('journals.csv', 'w') as file:
        writer = csv.writer(file)
        for name in tnames_sorted:
            writer.writerow([name])
            
def read_biblio_python(bname, min_count = 1):
    """Reads bibliography data the pythonic way"""
    db = pd.read_csv(bname)

    titles = list(db["Publication Title"])
    
    titles_unique = sorted(list(set(titles)))
    nu = len(titles_unique)
    counts = np.zeros(nu)
    
    for j in range(nu):
        counts[j] = titles.count(titles_unique[j])
        
    assert(counts.sum()==len(titles))
    # Remove those that are one or less counts
    
    tl = list(zip(titles_unique, list(counts)))
    tl = list(filter(lambda x: x[1]>min_count, tl))
    tl.sort(key = lambda x:1/x[1])
    
    tnames = [w[0] for w in tl]
    tcount = [int(w[1]) for w in tl]
    return tnames, tcount

def read_biblio_sqlite(sqname, min_count = 1):
    """Reads bilbiography from sqlite files directly"""
    conn = sqlite3.connect(sqname)
    con = conn.cursor()
    con.executescript( 
            """
            CREATE TEMPORARY TABLE IF NOT EXISTS tmp(field1 TEXT);
    
            INSERT INTO tmp SELECT 
            	itemDataValues.value 
            FROM 
            	itemData, itemDataValues 
            WHERE 
            	itemData.fieldID = 12  AND itemData.valueID = itemDataValues.valueID ;
            """
            )
    
    tl =  list(con.execute("SELECT field1, count(*) FROM tmp GROUP BY field1;"))
    tl = sorted(tl,key=lambda x:1/x[1])
    tl = list(filter(lambda x: x[1]>min_count, tl))
    tnames = [w[0] for w in tl]
    tcount = [int(w[1]) for w in tl]
    return tnames, tcount

sqname = 'zotero_1105.sqlite'
tnames, tcount = read_biblio_sqlite(sqname)

journals_dict = {}
with open('journals_type.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        journals_dict[row[0]] = row[1]
        # replace with abbreviation
        if len(row[2])>0:
            abb = row[2]
            ii = tnames.index(row[0])
            tnames[ii] = abb
            journals_dict[row[2]] = row[1]
            
nmax = 20
ttl = tnames[:nmax]
tct = tcount[:nmax]



plt.figure(figsize = (4,4))
plt.bar(ttl,tct)
plt.ylabel("Nr references")

plt.xticks(rotation=70)
plt.tight_layout()

ax = plt.gca()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.savefig("bar_journals.png")

# Nr of occurences of different subfields
jtypes = list(set(journals_dict.values()))
ntypes = len(jtypes)
counts = [0 for w in jtypes]
jtypes_dict = dict(zip(jtypes,counts))

for j in range(len(tnames)):
    count = tcount[j]
    name = tnames[j]
    if name in journals_dict:
        jtype = journals_dict[name]
    else:
        if "unknown" not in jtypes_dict.keys():
            jtypes_dict["unknown"] = 0
        jtype = "unknown"
    jtypes_dict[jtype] += count
    
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = jtypes_dict.keys()
sizes = [jtypes_dict[w] for w in jtypes_dict.keys()]
explode = [0.0]*len(labels)

fig1, ax1 = plt.subplots(figsize = (4,4))
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', explode = explode,
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.tight_layout()
plt.savefig("pie chart.png")
    
