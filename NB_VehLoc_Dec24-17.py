
# coding: utf-8

# In[16]:


def whitney(reqtime, routenum, filedate):
    ###Requests vehicle locations from the NextBus API and writes these to a text file###
    import requests
    import json
    
    #Paremeters - to be moved out of function, eventually
    parameters1 = {"a": "ttc", "r": routenum, "t": reqtime}

    #Request the feed results
    r1 = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations", params=parameters1)
    r1.raise_for_status()

    data1 = r1.json()
    VehDat = data1['vehicle']

    #Creates a list containing 'w' lists, each of 'h' items, all set to 0
    w = 6
    h = len(VehDat)   #reads list length and assigns to h
    VehRes = [[0 for x in range(w)] for y in range(h)] 

    #Write results to VehRes matrix
    for i in range (0, h):
        VehRes[i][0] = VehDat[i]['id']
        VehRes[i][1] = VehDat[i]['lat']
        VehRes[i][2] = VehDat[i]['lon']
        VehRes[i][3] = VehDat[i]['heading']
        VehRes[i][4] = VehDat[i]['secsSinceReport']
        VehRes[i][5] = reqtime
          
    with open('NextBusOutput-Route{0}-{1}.txt' .format(routenum, filedate), 'a') as outfile:  
        json.dump(VehRes, outfile)
        


# In[17]:


def main():
    import time 
        
    #1 hour = 120 rounds
    #2 hour = 240 rounds
    
    rounds = 3
    counter = 0
    
    # TTC route number
    routenum = "501"
    
    # file date for naming of text file, day month year - dayname AM/PM
    filedate = time.strftime("%d%b%Y-%a%p")
        
    while counter < rounds:
         
        tic = time.time() #counter start
                
        times = time.time() * 1000
        times = int(times)
        reqtime = times - 30000 

        whitney(reqtime, routenum, filedate)
                
        counter = counter + 1
        print(counter)
        
        toc = time.time() #counter end
        delay = (toc - tic) #function delay
                              
        time.sleep(2 - delay)


# In[18]:


main()

print("Done")

