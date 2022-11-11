from sqlalchemy import insert
import models
import requests
import datetime
import yaml
from sqlalchemy import create_engine
import shutil

# Load the config file.
with open("config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)

#Created the connection of DB.
DATABASE_URI = "postgresql://" + data['database']['username'] + ":" + data['database']['password'] + "@localhost/"+ data['database']['db']
engine = create_engine(
    DATABASE_URI,    pool_pre_ping=True, 
)

#API of countries, State, and Cities.
county_url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates%2Bcities.json?name"
image_url = "https://restcountries.com/v2/all"


#This function is responsible for Countries.
def post_countries():
        response = requests.get(f"{county_url}")
        response1 = requests.get(f"{image_url}")


        coun = response.json()
        ur = response1.json()

        for i in coun :
            for j in ur:
                if i['name'] == j['name']:
                    print(i['name'] ,"  " ,  j['flag'], "###########")
                    
                    
                    res = requests.get(j['flag'], stream = True)

                    if res.status_code == 200:
                        with open(f"countries_images/{i['name']}.svg" ,'wb') as f:
                            shutil.copyfileobj(res.raw, f)
                        print('image  download: ',i['name'])

                        data = (
                            insert(models.Countries).
                            values(name=i['name'], 
                                   flag_image=f"countries_images/{i['name']}.svg", 
                                   status = True ,
                                   created_at =datetime.datetime.utcnow() ,
                                   updated_at =datetime.datetime.utcnow() )
                        )
                        result = engine.execute(data)    
                                               
# post_countries()



import time
# This function is responsible for State
def post_state(country_name , loop_count):
        response = requests.get(f"{county_url}")


        print("sucessfully fetched the data")
        coun = response.json()


        for i in coun :
            if i['name'] == country_name:
                try :
                    
                    for  k in i['states']:
                        print(k['name'])

                        data = (
                            insert(models.States).
                            values(name=k['name'], 
                                    countries_id =  loop_count,
                                    status = True ,
                                    created_at =datetime.datetime.utcnow() ,
                                    updated_at =datetime.datetime.utcnow() )
                        )
                        result = engine.execute(data)    
                        print(result)
                        print("###########################")
                        print(k['name'] , "Insert into database")
                
                except:
                    print("data not found ")
                    
# for i in range(1 , 205):
        
#     rs = engine.execute(f'SELECT * FROM Countries Where id = {i}')
#     for j in rs:
#         print(j.name , " : This is a Coutry name" , i)
#         post_state(j.name , i)
 
            
            
            
response = requests.get(f"{county_url}")  
#This Function is responsible for Cities.       
def post_cities(state_name , loop_count):
        

        coun = response.json()
        try :
                
            for i in coun :
                for j in i['states']:
                    if j['name']==state_name:
                        for  k in j['cities']:
                            # print(k['name'] , ":" , loop_count)
                            
                                print("###")
                                print(k['name'] ," : " ,j['name'] , " : ",loop_count)
                                
                                data = (
                                        insert(models.Cities).
                                        values(name=k['name'], 
                                                state_id =  loop_count,
                                                status = True ,
                                                created_at =datetime.datetime.utcnow() ,
                                                updated_at =datetime.datetime.utcnow() )
                                )
                                result = engine.execute(data)    
                                print(result)
                                print(j['name'] , "Insert into database    :   " ,loop_count )
                                                  
                            
        except:
            print("Something wrong")
                
            # for j in i :
            #         print(j['name'])
            #         try :  
            #             for i in i['name']:
            #                 print(i['name'])
                    # for  k in i['states']:
                    #     for j in k['cities'] :
                    #         print(j['name'])
                        
                        # data = (
                        #     insert(models.Cities).
                        #     values(name=j['name'], 
                        #             state_id =  loop_count,
                        #             status = True ,
                        #             created_at =datetime.datetime.utcnow() ,
                        #             updated_at =datetime.datetime.utcnow() )
                        # )
                        # result = engine.execute(data)    
                        # print(result)
                        # print(j['name'] , "Insert into database    :   " ,loop_count )
                        # time.sleep(0.5)
                    # except:
                    #     print("data not found ")
                
  
for loop_count in range(1, 4067):
        
    rs = engine.execute(f'SELECT * FROM States Where id = {loop_count}')
    for z in rs:
        print(z.name , " : This is a State name" , loop_count)
        post_cities(z.name , loop_count)
 

            

            
# response = requests.get(f"{county_url}")

# coun = response.json()


# for i in coun :
#     if i['name'] == 'Afghanistan':
        
#             for  k in i['states']:
#                 for j in k['cities'] :
#                     print(j['name'])
                
    
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            

# url = "https://upload.wikimedia.org/wikipedia/commons/5/5c/Flag_of_the_Taliban.svg" #prompt user for img url
# file_name ='countries_images/Save.svg' #prompt user for file_name

# res = requests.get(url, stream = True)

# if res.status_code == 200:
#     with open(file_name,'wb') as f:
#         shutil.copyfileobj(res.raw, f)
#     print('Image sucessfully Downloaded: ',file_name)
    
    
    
# #     with ZipFile('countries_images/Save.zip', 'r') as zipObj:
# #    # Extract all the contents of zip file in current directory
# #         zipObj.extractall()
# else:
#     print('Image Couldn\'t be retrieved')
