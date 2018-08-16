# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 11:48:24 2018

@author: HDL feat.SXH
"""

import datetime
from datetime import timedelta        
import csv
from geopy.distance import vincenty
import time
import pprint
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psycopg2
import pandas as pd
import pandas.io.sql as psql

# -----------------------------------------------------SQL PART -----------------------------------------------------------
try:
        conn = psycopg2.connect(host="10.1.2.146", database="VehLoc", user="postgres", password="postgres")
except:
        print("Error: Unable to establish database connection.")
    
cur = conn.cursor()
cur.execute("SELECT * FROM epoch_collection_pm_2018 WHERE routenum = '501' AND secssincereport < 21")
table = cur.fetchall()



# --------------------------------------------------------------------------------------------------------------------------
"""
         f_latdiff = abs(float(row[1])- f_lat)
         f_longdiff = abs(float(row[2])-f_long)
         l_latdiff = abs(float(row[1])-l_lat)
         l_longdiff = abs(float(row[2])-l_long)
"""

### INPUT latitude and longitude for First and Last station

f_lat = 43.652454
f_long = -79.379085
l_lat = 43.642118
l_long = -79.429202

# Set a threshold
threshold_radius = 50

# reads data from csv file
"""
print('vehicle ID'," ",'time',"  ",'first stop diff',"  ",'last stop diff')
with open('NextBusOutput-Route501-20Jul2018-FriAM.csv','r') as f:
    reader = csv.reader(f)
    dataset = []
"""


#--------------------------------------------------------------------------------------------------------------------------
    
# conversion of time and computing distance between the vehicle and First/Last stop
#pprint.pprint(table)
dataset = []
for row in table:
    converted = int(row[5])/1000 - int(row[4])
    epoch = datetime.datetime.fromtimestamp(converted)
    epoch_est = epoch - timedelta(hours=4)
    distance_btwn_first_stop = vincenty((row[1],row[2]),(f_lat,f_long)).meters
    distance_btwn_last_stop = vincenty((row[1],row[2]),(l_lat,l_long)).meters
    dataset.append([row[0],epoch.strftime('%H:%M:%S'),distance_btwn_first_stop,distance_btwn_last_stop])

   
     
# Sort it by vehicle ID
dataset.sort(key=lambda x: x[0])    


# Filtering out the rows thats neither First or Last stop (filter out of range rows)
filtered_data = [row for row in dataset if row[2] < threshold_radius or row[3] < threshold_radius]


# Indexing vehicles that successfully left the First stop and arrived on Last Stop 
for i in range(0, len(filtered_data)):
    if i < len(filtered_data)-1:
        
        if filtered_data[i][2] < threshold_radius and filtered_data[i+1][3] < threshold_radius:
            filtered_data[i+1].append("Gucci")
        else:
            filtered_data[i+1].append("Nope")



          
# Converting Time(string) to number
            
for i in range(0, len(filtered_data)):
    filtered_data[i][1] = sum(int(x) * 60 ** i for i,x in enumerate(reversed(filtered_data[i][1].split(":")))) 
    
   

# Calculating the Travel time for valid trips
total_num_trips = 0
sum_of_valid_trips = 0
tt_list = []
actual_time = []
for i in range(0, len(filtered_data)):
    if i > 0:
        
        if filtered_data[i][4] == "Gucci" and filtered_data[i][0] == filtered_data[i-1][0]:
            filtered_data[i].append(((((float((filtered_data[i][1]))-float((filtered_data[i-1][1])))/60))))
            total_num_trips = total_num_trips + 1
            sum_of_valid_trips = sum_of_valid_trips + filtered_data[i][5]
            
# Seperate only travel times & actual time in a single list            
            tt_list.append(filtered_data[i][5])
            actual_time.append(filtered_data[i][1])
        else:
            filtered_data[i].append(0)


avg_travel_time = sum_of_valid_trips/total_num_trips



# Percentile Calculation
tt = np.array(tt_list)
p_5 = np.percentile(tt,5)
p_95 = np.percentile(tt,95)        


# Plotting
at = np.array(actual_time)
fig, ax = plt.subplots()
plt.plot(at,tt,'bo')

formatter = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%H:%M:%S', time.gmtime(s)))
ax.xaxis.set_major_formatter(formatter)
plt.title('Travel Time Calculator!!!')
plt.xlabel('Departure Time')
plt.ylabel('Duration (Minutes)')

# Setting x-y limits for graphs
#ax.set_xlim([datetime.time(0,0,0),datetime.time(17,00,59)])

ax.set_ylim([0,120])
plt.show()


### Used to write csv file (ignore)
"""

with open("Test Ouput.csv","a") as f:
    writer = csv.writer(f, dialect ='excel')   
    writer.writerow(filtered_data)
"""

pprint.pprint(filtered_data)
print('Total Valid Trips:',total_num_trips)
print('Average Travel Time:',avg_travel_time,'Minutes') 
print('5th Perecentile Traveltime:',p_5)       
print('95th Percentile Traveltime:', p_95)
#pprint.pprint(table)

