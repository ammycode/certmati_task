import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as t
import json
import unicodedata



#unicoding function to remove codes
def uni_(a):
    return(unicodedata.normalize("NFKD",a))

#beautifulsoup based data exrator to get all the required data
def data_excractor(url):
    d_dict=dict()
    result=requests.get(url)
    soup=BeautifulSoup(result.text,'html')
    title=soup.find('h1',class_='job-title',itemprop='title').text
    d_dict['title']=title
    location= soup.find('spl-job-location').get('formattedaddress')
    d_dict['location']=location
    x=BeautifulSoup(str(soup.find(itemprop='responsibilities')),'html.parser')
    description=list(map(uni_,list(x.strings)))    
    d_dict['description']=description
    y=BeautifulSoup(str(soup.find(itemprop='qualifications')),'html.parser')
    qualifications=list(map(uni_,list(y.stripped_strings)))
    d_dict['qualifications']=qualifications
    job_type=soup.find('li',class_='job-detail',itemprop="employmentType").text
    d_dict['job_type']=job_type

    return (d_dict)


#selenium based web crawler to execute and exract all data
#worst time performance - 2mins 
def driver_():
    options=Options()
    options.add_argument('--headless')
    # open driver in headless mode
    driver= webdriver.Edge(options=options)
    #start url as mentioned in task list
    start_url='https://www.cermati.com/karir'
    driver.get(start_url)
    driver.find_element(By.LINK_TEXT,'View All Jobs').click()

    data_dict={}
    #to modify the dynamic form getting field list
    z=driver.find_element(By.ID,'job-department')
    form_fields=z.text.strip().split('\n')[1:]
    #itterating over field list to get links and corresponding data
    for form_field in form_fields:
        innerlist=list()
        driver.find_element(By.ID,'job-department').send_keys(form_field)
        x=driver.find_element(By.CLASS_NAME,'fa-angle-right')
        y=x.find_element(By.XPATH,"./..")
        while True:
            
            inner_dict = {}
            
            buttons = driver.find_elements(By.LINK_TEXT, "Apply")
            #done as to counter a realtime error of form not loading properly.
            t.sleep(1)
            for button in buttons:
            # Check if the button text is "Apply"
                if button.text == "Apply":
                    # Get the value of the href attribute
                    link = button.get_attribute("href")
                    inner_dict=data_excractor(link)
                    innerlist.append(inner_dict)
                    
            
            if y.is_enabled() is True:
                WebDriverWait(y, 30).until(EC.element_to_be_clickable(y)).click()
            else:
                break
        data_dict[form_field]=innerlist
    
    driver.close()                
    return(data_dict)

scraper=driver_()
json_obj=json.dumps(scraper,indent=1)
with open(r"op.json",'w',encoding='utf-8') as out:
    out.write(json_obj)