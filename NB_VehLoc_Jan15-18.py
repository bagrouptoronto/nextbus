# coding: utf-8

# In[1]:


def whitney(reqtime, routenum, outfile):
    ###Requests vehicle locations from the NextBus API and writes these to a text file###
    
    import requests
    import json    
    
    #Paremeters
    whitneyparams = {"a": "ttc", "r": routenum, "t": reqtime}

    #Request the feed results
    r1 = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations", params=whitneyparams)
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
        outfile.write("{},{},{},{},{},{}\n".format(VehRes[i][0],VehRes[i][1],VehRes[i][2],VehRes[i][3],VehRes[i][4],VehRes[i][5]))       


# In[2]:


def houston(status):
    import requests
    
    slack_token = "xoxb-300357605111-BXLtH8nz46x9S6qFev7SvsyC"
    
    if status == "initialize":
        text = "NextBusAPI ready for launch"
    if status == "success":
        text = "we have liftoff :grinning:"
    if status == "fail":
        text = "we have a problem :anguished:"
      
    channel = "#api_test"
    #Paremeters
    houstonparams = {"token": slack_token, "channel": channel, "as_user": "true", "text": text}

    #Slack message request line
    r1 = requests.get("https://slack.com/api/chat.postMessage?", params=houstonparams)
    r1.raise_for_status()


# In[3]:


def main():
    import time
        
    houston("initialize")
    
    # Standard Params
    rounds = 3
    counter = 0
    timestep = 10
    
    # TTC route number
    routenum = "501"
    
    # file date for naming of text file, day month year - dayname AM/PM
    filedate = time.strftime("%d%b%Y-%a%p")
    with open('NextBusOutput-Route{0}-{1}.txt' .format(routenum, filedate), 'a') as outfile:
    
        while counter < rounds:
        
            tic = time.time() #counter start
        
            counter = counter + 1
            print(counter)         
        
            times = time.time() * 1000
            times = int(times)
            reqtime = times - (timestep*1000) 

            whitney(reqtime, routenum, outfile)
               
            toc = time.time() #counter end
            delay = (toc - tic) #function delay
                              
            time.sleep(timestep - delay)
            
    outfile.close()
    
    houston("success")


# In[4]:


main()

print("Done")
