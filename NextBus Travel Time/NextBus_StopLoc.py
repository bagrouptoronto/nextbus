
# coding: utf-8

# In[115]:


def bobby(routenum, outfile):
    ###Requests vehicle locations from the NextBus API and writes these to a text file###
    import requests
    import json
    
    #Paremeters
    bobbyparams = {"a": "ttc", "r": routenum}

    #Request the feed results
    r2 = requests.get("http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig", params=bobbyparams)
    r2.raise_for_status()

    data2 = r2.json()
    StopDat = data2['route']['stop']
        
    #Creates a list containing 'w' lists, each of 'h' items, all set to 0
    w = 4
    h = len(StopDat)   #reads list length and assigns to h
    StopRes = [[0 for x in range(w)] for y in range(h)] 

    #Write results to VehRes matrix
    for i in range (0, h):
        StopRes[i][0] = StopDat[i]['tag']
        StopRes[i][1] = StopDat[i]['title']
        StopRes[i][2] = StopDat[i]['lat']
        StopRes[i][3] = StopDat[i]['lon']
        outfile.write("{},{},{},{}\n".format(StopRes[i][0],StopRes[i][1],StopRes[i][2],StopRes[i][3]))       


# In[116]:


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
    r3 = requests.get("https://slack.com/api/chat.postMessage?", params=houstonparams)
    r3.raise_for_status()


# In[117]:


def main():
    import time
        
    houston("initialize")
          
    # TTC route number
    routenum = "501"
    
    # file date for naming of text file, day month year - dayname AM/PM
    filedate = time.strftime("%d%b%Y-%a%p")
    with open('NextBusStops-Route{0}-{1}.txt' .format(routenum, filedate), 'a') as outfile:
    
        bobby(routenum, outfile)
                
    outfile.close()
    
    houston("success")


# In[118]:


main()

print("Done")

