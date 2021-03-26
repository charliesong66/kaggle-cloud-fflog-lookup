# check OS version
!cat /etc/os-release

# check current directory
!pwd
!ls -l

# show directory contents
!echo "ls -l /kaggle"
!ls -l /kaggle

!echo "\nls -l /kaggle/working"
!ls -l /kaggle/working

!ls -l "../input/firefox-63.0.3.tar.bz2/"

# COPY OVER FIREFOX FOLDER INTO NEW SUBFOLDER JUST CREATED
!cp -a "../input/firefox-63.0.3.tar.bz2/firefox" "../working"
!ls -l "../working/firefox"

# ADD READ/WRITE/EXECUTE CAPABILITES
!chmod -R 777 "../working/firefox"
!ls -l "../working/firefox"

# INSTALL PYTHON MODULE FOR AUTOMATIC HANDLING OF DOWNLOADING AND INSTALLING THE GeckoDriver WEB DRIVER WE NEED
!pip install webdriverdownloader

# INSTALL LATEST VERSION OF THE WEB DRIVER
from webdriverdownloader import GeckoDriverDownloader
gdd = GeckoDriverDownloader()
gdd.download_and_install("v0.23.0")

# INSTALL SELENIUM MODULE FOR AUTOMATING THINGS
!pip install selenium

# LAUNCHING FIREFOX, EVEN INVISIBLY, HAS SOME DEPENDENCIES ON SOME SCREEN-BASED LIBARIES
!apt-get install -y libgtk-3-0 libdbus-glib-1-2 xvfb

# SETUP A VIRTUAL "SCREEN" FOR FIREFOX TO USe
!export DISPLAY=:99
    
print('**************')
print('** COMPLETE **')
print('**************')

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


from selenium import webdriver as selenium_webdriver
from selenium.webdriver.firefox.options import Options as selenium_options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as selenium_DesiredCapabilities

import pandas as pd
import numpy as np
import re


def print_table_fflog(first_name, last_name, server):
    
    
    ############### 
    # open driver #
    ###############
    browser_options = selenium_options()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--window-size=1920,1080")

    capabilities_argument = selenium_DesiredCapabilities().FIREFOX
    capabilities_argument["marionette"] = True

    browser = selenium_webdriver.Firefox(
        options=browser_options,
        firefox_binary="../working/firefox/firefox",
        capabilities=capabilities_argument
    )

    browser.get(f"https://www.fflogs.com/character/na/{server}/{first_name}%20{last_name}")

    ########################################################################################################################

    ############
    # get data #
    ############

    # boss name
    outerHTML = browser.find_element_by_xpath('//table[@id="boss-table-38"]').get_attribute('outerHTML')
    df = pd.read_html(outerHTML)[0]

    df.columns = ['Boss', 'best %', 'rDPS', 'kills', 'fastest', 'med', 'all_star', 'rank']
    df.drop(columns=['kills', 'fastest', 'med'], inplace=True)
    df['Boss'] = ['Cloud of Darkness', 'Shadowkeeper', 'Fatebreaker', 'Eden\'s Promise', 'Oracle of Darkness ']
    df

    # icon of class
    pics = browser.find_elements_by_xpath('//td[contains(@class, "rank-percent hist-cell")]//img')

    # difficulty of raid
    difficulty = browser.find_element_by_xpath('//div[@class="best-perf-avg"]//span[@class="primary"]')

    ########################################################################################################################

    # intialize
    used_jobs = []

    diff = difficulty.text


    # choose pic, get class name, split by -, last element is class
    for pic in pics:
        used_jobs.append(pic.get_attribute('class').split('-')[-1])    

    
    # loop used_jobs to fill JOB column
    job = []
    i = 0
    
    for perc in df['best %']:
        if perc != '-':
            job.append(used_jobs[i])
            i = i + 1
        else:
            job.append('-')
            
            
    # add job column to df        
    df['job'] = job    
    
    # rearrange columns
    df2 = df[['Boss', 'best %', 'job', 'rDPS', 'all_star', 'rank']]

    # output
    print(first_name, last_name, ',', server, ', **' , diff, '** ')
    print()
    print(df2)
    print('==========================================================')

    
def get_name_server(chat_msg):

    # split sentence
    temp = chat_msg.split('. ')

    # get first two words, firstname + lastname_Server
    temp2 = [line.split(' ')[:2] for line in temp]

    for item in temp2:
        # find server
        server_list = 'Behemoth|Excalibur|Exodus|Hyperion|Lamia|Leviathan|Ultros'
        p = re.compile(server_list)
        server = p.findall(item[1])

        # default server YOU are on
        # if no server, server = Famfrit
        if len(server) > 0:        
            # str name of server   
            server_name = server[0]
        else:
            server_name = 'Famfrit'


        item[1] = item[1].replace(server_name, '')
        item.append(server_name)
    
    return temp2   
  
########################################################################################################################  
# start here , paste in chat msg
chat_msg = input('insert chat:')
print('***************************************************')
print('***************************************************')

people_to_lookup = get_name_server(chat_msg)

for person in people_to_lookup:
    first_name = person[0]
    last_name = person[1]
    server = person[2]
    
    try:
        print_table_fflog(first_name, last_name, server)
    except:
        print('Error:', first_name, last_name, server)  

#######################################################################################################################
