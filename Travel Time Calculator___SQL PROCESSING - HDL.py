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
# Change database or user if the data is stored in a different database.
try:
        conn = psycopg2.connect(host="10.1.2.146", database="VehLoc", user="postgres", password="postgres")
except:
        print("Error: Unable to establish database connection.")
    
cur = conn.cursor()
# Pick a Route number and change it below
# Also change SQL table name below if the data is stored in a different table Ex) "SELECT * FROM 'Your table name bro'
cur.execute("SELECT * FROM epoch_collection_pm_2018 WHERE routenum = '501' AND secssincereport < 21")
table = cur.fetchall()

# --------------------------------------------------------------------------------------------------------------------------

### INPUT latitude and longitude for First and Last station Ex) Grab two location (bus stop/intersection) you are interested

f_lat = 43.652454
f_long = -79.379085
l_lat = 43.642118
l_long = -79.429202

# Set a threshold (in meters)
threshold_radius = 50

# reads data from csv file (kinda ignore since we are reading from an SQL table now)
"""
print('vehicle ID'," ",'time',"  ",'first stop diff',"  ",'last stop diff')
with open('NextBusOutput-Route501-20Jul2018-FriAM.csv','r') as f:
    reader = csv.reader(f)
    dataset = []
"""


#---------------------------------------------------------Calculation script starts here--------------------------------------------
    
# conversion of time and computing distance between the vehicle and First&Last stop

dataset = []
for row in table:
# On the SQL table, column 6 is in miliseconds, so we would need a conversion to seconds, then subtract it by column 5 which is seconds since report to get actual time
    converted = int(row[5])/1000 - int(row[4])
# NextBus Script spits out times in epoch time, so we would need conversion
    epoch = datetime.datetime.fromtimestamp(converted)
# Change to EST time
    epoch_est = epoch - timedelta(hours=4)
# Vincenty function tells you the difference between 2 sets of latitude and longitude
    distance_btwn_first_stop = vincenty((row[1],row[2]),(f_lat,f_long)).meters
    distance_btwn_last_stop = vincenty((row[1],row[2]),(l_lat,l_long)).meters
    
# I just added 4 columns in a table called dataset
    dataset.append([row[0],epoch.strftime('%H:%M:%S'),distance_btwn_first_stop,distance_btwn_last_stop])

   
     
# Sort it by vehicle ID
dataset.sort(key=lambda x: x[0])    


# Filtering out the rows thats neither First or Last stop (filter out of range rows)
filtered_data = [row for row in dataset if row[2] < threshold_radius or row[3] < threshold_radius]


# Indexing vehicles that successfully left the First stop and arrived on Last Stop 
for i in range(0, len(filtered_data)):
    if i < len(filtered_data)-1:
# If the row i is the first stop and the next row i+1 is matched as last stop, it means a valid trip (Check excel Travel Time calculator for better understanding)
        
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
# Finds the "Gucci" row and also checks if the previous row is the same vehicle ID#        
        if filtered_data[i][4] == "Gucci" and filtered_data[i][0] == filtered_data[i-1][0]:
# Grabs the time found for the vehicle at the last stop and first stop and subtracting it
            filtered_data[i].append(((((float((filtered_data[i][1]))-float((filtered_data[i-1][1])))/60))))
# Couting if the trip was valid            
            total_num_trips = total_num_trips + 1
# Need thsi to calculate average travel time later on
            sum_of_valid_trips = sum_of_valid_trips + filtered_data[i][5]
            
# Seperate only travel times & actual time in another empty table I created up there           
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

