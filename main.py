import email
from optparse import Option
from pickle import NONE
from sqlite3 import Date
from sys import intern
from unittest.util import strclass
from xmlrpc.client import Boolean
from fastapi import FastAPI , Request,Depends ,Form, Body ,  File , UploadFile , status , HTTPException , Response
import database
import models
from sqlalchemy.orm import Session
import schema
from datetime import datetime, timedelta
from typing import Optional, Union 
import shutil
from pydantic import SecretStr , EmailStr , conint
from sqlalchemy import  BIGINT, JSON, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import smtplib , ssl
from email.message import EmailMessage


import email_validator as  _email_check 
from fastapi.middleware.cors import CORSMiddleware
import validation 
import yaml
import uuid


from fastapi.responses import JSONResponse
import services as _services
import schema as _schema
import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
import passlib.hash as _hash

# database.configuration()

app = FastAPI()


origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



with open("config.yaml", "r") as yamlfile:
    config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

models.Business_categorys.metadata.create_all(database.engine) # create database when you create your models
models.Business_sub_categorys.metadata.create_all(database.engine)
def get_db():
    db = database.SessionLocal()
    try :
        yield db 
    finally:
        db.close()

# for current dateand time 
now = datetime.now()
current_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

#this instance/API is for category upload 
@app.post('/category/', status_code=status.HTTP_201_CREATED)
async def Business_category_function(request : schema.category ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    #This is for name validation.
    
    data = db.query(models.Business_categorys).filter(models.Business_categorys.name == request.name ).first()
    if data : 
        if data.status == True :
            
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"Category {request.name} already exist"},)
        

    name_validation = validation.name_validation(request.name)
    if name_validation == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": f"Name Field is Required"},)

    #validation for length validation. 
    length_validation = validation.length_validation(request.name)
    if length_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Category name should be greterthan 2 character"},)
    
    
    Business_category_post = models.Business_categorys(
        name = request.name ,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_category_post)
    db.commit()
    db.refresh(Business_category_post)
    
    # We need this data in list data type for passing data into front-end
    # business_category_type_change = [ i  for i in  Business_category_post]
    data = []
    data.append(Business_category_post)
    return {
            "Item": data,
            "message" : "Successful"
            }


# thsi api is  for update category 




@app.put('/category/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def category_update(id : int,  request : schema.category , db : Session = Depends(get_db) ):
    fetch_data_category  = db.query(models.Business_categorys).filter(models.Business_categorys.id == id )
    print(fetch_data_category.exists())
    if not fetch_data_category.first(): 
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= f'blog with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": f"Data with this id : {id} not found"})
        
    else:
        # validation if for name value can not be null.
        name_validation = validation.name_validation(request.name)
        if name_validation == True:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": f"Name Field is Required"},)

        # This validation is check for length gretter than 2 character.
        length_validation = validation.length_validation(request.name)
        if length_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Category name should be greterthan 2 character"},)

        # This validation is check for the name should be string
        integer_check = validation.int_check(request.name)
        if integer_check == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": " Name field should be string not Integer"},)
        # This validation is check for the id is deleted or not.
        
        deletedatacheck = validation.delete_datacheck(id , db)
        if deletedatacheck == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Category with this id : {id} not found "},)
            
        
        data1 = db.query(models.Business_categorys).filter(models.Business_categorys.name == request.name).first()
        if data1:
            if data1.status ==  False : 
                fetch_data_category = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).update(dict(name = request.name ,updated_at =  current_time ))
                db.commit()
                data =  db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).first()
                data1 = []
                data1.append(data)
                return    {
                    
                    "Item" :data1 ,
                    "message" : 'Successful'
                    
                    
                    }    
                
            else :
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"{request.name} already exist"},)
        else:
            fetch_data_category = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).update(dict(name = request.name ,updated_at =  current_time ))
            db.commit()
            data =  db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).first()
            
            data1 = []
            data1.append(data)

            # We need this data in list data type for passing data into front-end
            return  {
                    "Item" :data1 ,
                    "message" : "Successful"
                }  


# this is for detele post
@app.delete('/category/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_category = db.query(models.Business_categorys).filter(models.Business_categorys.id == id)
    if not delete_data_category.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.deletecheck (id , db)
    if check == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"Category with this id : {id} not found "},)

    delete_data_category = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)



# This is for return all data from category 


@app.get('/category/' , status_code=status.HTTP_200_OK)
async def  fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user) , page_num : int = 1 , page_size : int = 10  ):
    
    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_categorys).filter(models.Business_categorys.status ==  True).order_by(models.Business_categorys.id.desc())

    
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": 'No Category Available '},)
        
    total_pages = (result.count() / page_size)

    
    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
            
            

        return  {
            
            'Items' : data[start : end] , 
            "page" :  page_num , 
            "perPage" : page_size , 
            "totaldata" : result.count(),
            "totalPages" : total_pages,
            "message"  : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "page" :  page_num , 
            "perPage" : page_size , 
            "totaldata" : result.count(),
            "totalPages" : int(total_pages + 1),
            "message"  : "Successful"
            }





#This is for return single data from category 
@app.get('/category/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    

    
    new_blog = db.query(models.Business_categorys).filter(models.Business_categorys.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Category  with this id : {id} not found'},)
    
    
    #validation for check the id delete or not.
    check = validation.deletecheck (id , db)
    if check == True :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Category  with this id : {id} not found"},)
    
    # We need this data in list data type for passing data into front-end
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
            "Item" : new_blog1,
            "message" : "Successful"
            }


# This API is Responsible for get all subcategory by category ID.
@app.get("/subcategory_by_category_id/{category_id}/", status_code=status.HTTP_200_OK)
def city_get_all(category_id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    
    #validation for country 
    if category_id == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business_Category Available'},)
    check_category_id = db.query(models.Business_categorys).get(category_id)
    if not check_category_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business_Category Available'},)
        

    result = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.business_category_id ==  category_id)
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Subcategory Available'},)

    new_list = []
    for i in result:
        new_list.append(i)
        
    return  {
        
        'Items' : new_list, 
        "message"  : "Successful"
        
        }
# this post request is for add subcategory 
@app.post('/sub_category/' , status_code=status.HTTP_201_CREATED)
async def  Business_sub_category_function(request : schema.sub_category,user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), ):
    # validation for name not null.
    check_name = validation.name_validation(request.name)
    if check_name == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Name field required "},)

    # validation for name length.
    check_length = validation.length_validation(request.name)
    if check_length == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Category name should be greterthan 2 character"},)

    #validation for category id is not zero
    check_category = validation.id_check(request.business_category_id)
    if check_category == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Business_category id with this id : {request.business_category_id} not found '},)

    business_id_check = db.query(models.Business_categorys).filter(models.Business_categorys.id == request.business_category_id)
    if not business_id_check.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category id with this id : {request.business_category_id} not found '},)
    
    if business_id_check.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category id with this id : {request.business_category_id} not found '},)
        
    
    
    name_check = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.name == request.name).first()

    if name_check:
        if name_check.status == True :
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f'Sub_category {request.name} already exist'},)


    data = db.query(models.Business_categorys).filter(models.Business_categorys.id ==request.business_category_id ).first()
    
    check_exist_or_not = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.name == request.name )
    if check_exist_or_not.first():

        
        if check_exist_or_not.first().status == True:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Sub_category_name already exist'},)
        
    if data:
        Business_sub_category_post = models.Business_sub_categorys(
        name = request.name ,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time ,
        business_category_id =  request.business_category_id , 
        )

        db.add(Business_sub_category_post)
        db.commit()
        db.refresh(Business_sub_category_post)
        # We need this data in list data type for passing data into front-end
        Business_sub_category_post1 = []
        Business_sub_category_post1.append(Business_sub_category_post)
        return {
                "Item" :Business_sub_category_post1 ,
                "message" : "Successful"
                } 
    
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Category id:{request.business_category_id} does not exist'},)
    

# This request is for update sub_category 
@app.put('/sub_category/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def category_update(id : int,  request : schema.sub_category,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    
    # check id is available or not in Business_sub_categorys table 
    fetch_data_subcategory  = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id )
    print(fetch_data_subcategory.exists())
    if not fetch_data_subcategory.first():

        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'blog with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Business_sub_categorys with this id : {id} not found '},)

    else:
        # This is for name validation.
        checkname = validation.name_validation(request.name)
        if checkname == True:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": " Name Field Required"},)
        
        
        # This is for length validation
        check_length = validation.length_validation(request.name)
        if check_length == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Category name should be greterthan 2 character"},)


        data = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id).first()
        if data.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f" Business_sub_categorys Id with this  id : {id} not found "},)
        

        if request.business_category_id == 0 :
            # raise _fastapi.HTTPException(status_code=404 , detail= 'Enter sub_category id ')
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Enter sub_category id'},)

        
        
        
        name_check = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.name  == request.name).first()
        try :
                
            if name_check.status == True :
                print("prakah")
                if id != name_check.id:
                    return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":f'Subcategory {request.name} already exist '},)
                    
                if name_check.business_category_id == request.business_category_id :
                    return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":f'Subcategory {request.name}  already exist '},)
            
        except :
            pass
        # name_check = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.name == request.name).first()
        
        # print(request.business_category_id , "comiing from schema")
        # print(name_check.business_category_id , "coming from db")
        

        # if name_check.business_category_id == request.business_category_id :
        #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Subcategory name already exist '},)
             
        # if name_check.status == True:
        #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Subcategory name already exist '},)
        
        
        # check foregnkey is available or not in category table
        
        

        fetch_data_subcategory = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id ).update(dict(name = request.name , business_category_id= request.business_category_id,updated_at =  current_time ))
        db.commit()
        data =  db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id ).first()
        
        # We need this data in list data type for passing data into front-end
        data1 = []
        data1.append(data)
        return {
                "Item" :data1,
                "message" : "Successful"
                }
        # else:
        #     # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Category id:{request.business_category_id} does not exist ')
        #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Category id:{request.business_category_id} does not exist '},)
            
            

#This request is for delete subcategory 
@app.delete('/sub_category/{id}/', status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    delete_data_sub_category = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id)
    if not delete_data_sub_category.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " : f'blog with this id {id} not found '},)
    
    # This validation is check for id status should be true 
    data = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id ).first()
    if data.status == False:
        # raise _fastapi.HTTPException(status_code=404 , detail= f"{id} already Deleted") 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Business_sub_category with this id : {id} not found "})
        
        
    delete_data_sub_category = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id ).update(dict(status = False ))
    db.commit()
    # return  "data delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message " :  "Data delete successful"})



#This request is for return all data from subcategory 

@app.get('/sub_category/', status_code=status.HTTP_200_OK)
def all_category(user : _schema.User = _fastapi.Depends(_services.get_current_user) , page_num : int = 1 , page_size : int = 10,db : Session = Depends(get_db)):

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.status ==  True).order_by(models.Business_sub_categorys.id.desc())
    result2  = db.query(models.Business_categorys).filter(models.Business_categorys.id == 1)
    print(result)


    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " :  'No Sub_Category Available '},)




    if page_num < 0 or page_size < 0 :
            
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }


    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
            print(i.Business_category)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
            print(i.Business_category)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }





#This request is for return one data from subcategory 
@app.get('/sub_category/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " :  f'Data with this id {id} not found'},)
    
    # This validation is for check the data is already deleted or not
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " :  f'Data already deleted with this id : {id}'},)
        
    # We need this data in list data type for passing data into front-end
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
            "Item" : new_blog1 ,
            "message" : "Successful"
            } 



# This Instance/API is  for countries
@app.post('/country/',status_code=status.HTTP_201_CREATED)
async def Countries_function( user : _schema.User = _fastapi.Depends(_services.get_current_user),
    name : Union[str, None] = Body(default=...),
    file : UploadFile = File(...) ,
    db : Session = Depends(get_db), 
):
    check_name = validation.name_validation(name)
    if check_name == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": " Name Field Required"},)
    
    # This is for length validation
    check_length = validation.length_validation(name)
    if check_length == True:    
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Category name should be greterthan 2 character"},)
    try :
        
        data = db.query(models.Countries).filter(models.Countries.name == name).first()
        if data.status == True :
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"Country {name} already exist"},)
    except:
            
        with open("media/"+ file.filename , 'wb') as image :    
            shutil.copyfileobj(file.file , image)

        url = str('media/' + file.filename)
        
        print("UPLOAD")
        Countries_post = models.Countries(
            
            name = name ,
            flag_image = url ,
            status = True ,
            created_at= current_time , 
            updated_at= current_time                       
                                        )
        
        db.add(Countries_post)
        db.commit()
        db.refresh(Countries_post)
        
        # We need this data in list data type for passing data into front-end
        Countries_post1 = []
        Countries_post1.append(Countries_post)
        return {
                "Item" : Countries_post1,
                "message" : "Successful"
                }




@app.put('/country/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Countries_update(
    id : int , 
    name : Union[str, None] = Body( default=...),
    file : UploadFile = File(...) ,

    db : Session = Depends(get_db), 
):

    with open("media/"+ file.filename , 'wb') as image :
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    if id == 0 :
        # raise _fastapi.HTTPException(status_code=404 , detail= 'We can not proceed with 0')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Id not found '},)
    
    fetch_data_coutries = db.query(models.Countries).filter(models.Countries.id == id )
    if not fetch_data_coutries.first():
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)

    else:
        
        
        # This validation is for name 
        if name == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": " Name Field Required"},)
    
    # This is for length validation
        if len(name)  < 2 :
        # raise _fastapi.HTTPException(status_code=404 , detail= "Category name should be greterthan 2 character")
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Category name should be greterthan 2 character"},)
        print("!@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")
        data1 = db.query(models.Countries).filter(models.Countries.name == name).first()
        print("!@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!2", data1)
        if data1:
            
            if data1.status == True:
                print("!@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!3")
                
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"Countries {name} already exist "},)

        id_status_check = db.query(models.Countries).filter(models.Countries.id == id).first()
        if id_status_check.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)
            
        fetch_data_coutries = db.query(models.Countries).filter(models.Countries.id == id ).update(dict(name = name , flag_image = url ,updated_at =  current_time ))
        db.commit()
        data = db.query(models.Countries).filter(models.Countries.id == id ).first()

        
        data1 = []
        data1.append(data)
        return {
            "Item" : data1,
            "message" : "Successful"
            }


@app.delete('/country/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_contries= db.query(models.Countries).filter(models.Countries.id == id)
    if not delete_data_contries.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id {id} not found "},)
    
    delete_data_check = delete_data_contries.first()
    if delete_data_check.status == False :
        
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= "Data already deleted")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Data already deleted"},)
        
    delete_data_contries = db.query(models.Countries).filter(models.Countries.id == id ).update(dict(status = False))

    db.commit()
    # return "delete successful"
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Delete successful"},)




# This request is responsible for return all data from countries
@app.get('/country/', status_code=status.HTTP_200_OK)
def all_contries(  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):
    # new_blog =  db.query(models.Countries).all()
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Countries).filter(models.Countries.status ==  True).order_by(models.Countries.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "No Country available"},)


    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message"  : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message"  : "Successful"
            
            }




#This request is for return one data from contries 
@app.get('/country/{id}/' , status_code=status.HTTP_200_OK)
def by_id(id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Countries).filter(models.Countries.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
    
    #validation for get delete id 
    
    if new_blog.status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"This Id : {id} is already Deleted"},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return  {
            "Item" : new_blog1 , 
            "message" : "Successful"
            }







# This instance/ APi is for states  
@app.post('/state/', status_code=status.HTTP_201_CREATED)
async def state_function(request : schema.state, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db),):
    
    # Validation for name 
    name_validation_check = validation.name_validation(request.name)
    if name_validation_check == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Name field can not be blank"},)
    
    #length validation
    length_validation = validation.length_validation(request.name)
    if length_validation == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Length Should be Greterthan 2 character"},)
    
    #Id validation 
    id_validation = validation.id_check(request.countries_id)    
    if id_validation == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Countries with this id {request.countries_id} not found "},)
    
    check_data = db.query(models.States).filter(models.States.name == request.name)
    if check_data.first():
        if check_data.first().status == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Country {request.name} already exists "},)

    
    state_post = models.States(
    name = request.name ,
    countries_id = request.countries_id , 
    status  = True , 
    created_at = current_time , 
    updated_at = current_time ,

    )
    # check foregnkey available or not 
    check = db.query(models.Countries).filter(models.Countries.id == request.countries_id  ).first()
    if check  and check.status == True: 

        db.add(state_post)
        db.commit()
        db.refresh(state_post)
        
        state_post1 = []
        state_post1.append(state_post)
        
        return {
                "Item"  :state_post1,
                "message" : "Successful"
                }
    else :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Country id with this id : {request.countries_id} not found"},)
        

@app.put("/state/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.state, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.States).filter(models.States.id == id ).first()
    if data and data.status == True : 
    # Validation for name 
        name_validation_check = validation.name_validation(request.name)
        if name_validation_check == True:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Name field required"},)
        
        #length validation
        length_validation = validation.length_validation(request.name)
        if length_validation == True:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "Length Should be Greterthan 2 character"},)
        
        #Id validation 
        id_validation = validation.id_check(request.countries_id)    
        if id_validation == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Countries with this id : {request.countries_id} not found "},)
        
        check_data = db.query(models.States).filter(models.States.name == request.name)
        if check_data.first():
            if check_data.first().status == True :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Country {request.name} already exists"},)
                
        
        
        data = db.query(models.Countries).filter(models.Countries.id == request.countries_id)
        if data :
            if data.first().status == True :
                db.query(models.States).filter(models.States.id == id ).update(dict(name = request.name  ,countries_id =  request.countries_id  ,updated_at =  current_time ))
                db.commit()
                data = db.query(models.States).filter(models.States.id == id ).first()
                
                data1 = []
                data1.append(data)
                return {
                    "Item" : data1 , 
                    "message" : "Successful"
                    }
            else:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Countries with this id : {request.countries_id} not found '},)
             
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Countries with this  id : {request.countries_id} not found '},)
            

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
            
            
# @app.get("/state/", status_code=status.HTTP_200_OK)
# def state_get_all( user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):
    

#     start = (page_num -1) * page_size
#     end = start + page_size    
#     result = db.query(models.States).filter(models.States.status ==  True).order_by(models.States.id.desc())
#     if result.count() == 0 :
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No State Available'},)
        
#     if page_num < 0 or page_size < 0 :
#         new_list = []
#         for i in result:
#             new_list.append(i)
#             print(i.Countries)
            
#         return  {
            
#             'Items' : new_list , 
#             "message"  : "Successful"
            
#             }
#     total_pages = (result.count() / page_size)

#     if result.count() % int(page_size) == 0 :
        
#         print(total_pages, "total pages if block ")
#         data = []
#         for i in result:
#             data.append(i)
#             i.Countries
#         return  {
            
#             'Items' : data[start : end] , 
#             "Page" :  page_num , 
#             "PerPage" : page_size , 
#             "Totaldata" : result.count(),
#             "TotalPages" : total_pages,
#             "message" : "Successful"
            
#             }

#     else :
#         data = []
#         for i in result:
#             data.append(i)
#             i.Countries
            
#         return  {
            
#             'Items' : data[start : end] , 
#             "Page" :  page_num , 
#             "PerPage" : page_size , 
#             "Totaldata" : result.count(),
#             "TotalPages" : int(total_pages + 1),
#             "message"  : "Successful"
            
#             }



# This State API is updated API.
@app.get("/state/{C_id}/", status_code=status.HTTP_200_OK)
def state_get_all(C_id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    
    #validation for country 
    if C_id == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Country Available'},)
    check_country_id = db.query(models.Countries).get(C_id)
    if not check_country_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Country Available'},)
        

    result = db.query(models.States).filter(models.States.countries_id ==  C_id)
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No State Available'},)
    print(result.count(), "##################")
    new_list = []
    for i in result:
        new_list.append(i)
        
    return  {
        
        'Items' : new_list, 
        "message"  : "Successful"
        
        }





#This request is for return one data from state  
# @app.get('/state/{id}/' , status_code=status.HTTP_200_OK)
# def by_id(  id : int ,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
#     new_blog = db.query(models.States).filter(models.States.id == id).first()
#     if not new_blog:
#         # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found'},)
    
    
#     # This validation is for id is already deleted or not 
#     if new_blog.status == False:
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} already deleted'},)
        
#     new_blog1 = []
#     new_blog1.append(new_blog)
#     return {
#             "Item" : new_blog,
#             "message" : "Successful"
#             }

@app.delete('/state/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_state= db.query(models.States).filter(models.States.id == id)
    if not delete_data_state.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    if delete_data_state.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    delete_data_state = db.query(models.States).filter(models.States.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Data delete successful'},)
    
    # response.headers['delete_data'] = "data delete successful"

@app.post('/cities/', status_code=status.HTTP_201_CREATED)
async def cities_function(
    name : Union[str, None] = Body(default=...),
    state_id  : Union[int, None] = Body(default=...),
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db), 

):
    
    if state_id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found sdefsw'},)

    # validation for name can not be blank 
    name_validation_null_check = validation.name_validation(name)
    if name_validation_null_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Name field required'},)
    
    name_validation_length_check = validation.length_validation(name)
    if name_validation_length_check  == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Length Should be Greterthan 2 character'},)
    
    
    
    
    # check foregnkey id exist or not 
    data = db.query(models.States).filter(models.States.id == state_id )
    # if data.first()  and data.first().status == True:
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State {}'},)
    if not data.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id}  not found'},)
        
    data = db.query(models.Cities).filter(models.Cities.name == name )
    if data.first():
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":f'City {name} Already exist'},)
        
    

    cities_post = models.Cities(
        name = name ,
        state_id = state_id , 
        status  = True , 
        created_at = current_time , 
        updated_at = current_time ,
    )

    db.add(cities_post)
    db.commit()
    db.refresh(cities_post)
    
    cities_post1 = [] 
    cities_post1.append(cities_post)
    return  {
            "Item" : cities_post1,
            "message" : "Successful"
            }
    # else:
    #     # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'State id :{state_id} not found ')
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'State id :{state_id} not found '},)
    

@app.put("/cities/{id}/",status_code=status.HTTP_202_ACCEPTED)
def city_update(id : int,  request : schema.city,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_city = db.query(models.Cities).filter(models.Cities.id == id )

    check_data = db.query(models.Cities).filter(models.Cities.name == request.name)
    if check_data.first():
        if check_data.first().status == True :
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":f'City {request.name} already exist '},)
            
    
    
    if request.state_id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {request.state_id} not found sdefsw'},)

    if not fetch_data_city.first() :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found '},)
        
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'blog with this id : {id} not found ')
    else:

        data = db.query(models.Cities).filter(models.Cities.id == id ).first()
        if data.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
            
        
        
        # check the state id is available or not 
        check = db.query(models.States).filter(models.States.id == request.state_id)
        # validation.name_validation1(request.name)
        # validation.length_validation1(request.name)
        if not  check.first() and check.first().status == False:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id  :{request.state_id} not found '},)

            # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'State id :{request.state_id} not found ')
        else:
            fetch_data_city = db.query(models.Cities).filter(models.Cities.id == id ).update(dict(name = request.name  ,state_id =  request.state_id  ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Cities).filter(models.Cities.id == id ).first()
            
            data1 = []
            data1.append(data)
            return { 
                    "Item" : data1,
                    "message" : "Successful"
                    }



@app.delete('/cities/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_city= db.query(models.Cities).filter(models.Cities.id == id)
    if not delete_data_city.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found'},)
        
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
    
    if delete_data_city.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    delete_data_city = db.query(models.Cities).filter(models.Cities.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":'Delete data successfull '},)
    
    # return "delete data successfull "

# @app.get("/cities/", status_code=status.HTTP_200_OK)
# def city_get_all( user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):

#     start = (page_num -1) * page_size
#     end = start + page_size    
#     result = db.query(models.Cities).filter(models.Cities.status ==  True).order_by(models.Cities.id.desc())
#     if result.count() == 0 :
#         return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f'No City available '},)
#     if page_num < 0 or page_size < 0 :
#         new_list = []
#         for i in result:
#             new_list.append(i)
#             i.States
#             i.States.Countries
#         return  {
            
#             'Items' : new_list , 
#             "message"  : "Successful"
            
#             }      

#     total_pages = (result.count() / page_size)

#     if result.count() % int(page_size) == 0 :
        
#         print(total_pages, "total pages if block ")
#         data = []
#         for i in result:
#             data.append(i)
#             i.States
#             i.States.Countries

            
#         return  {
            
#             'Items' : data[start : end] , 
#             "Page" :  page_num , 
#             "PerPage" : page_size , 
#             "Totaldata" : result.count(),
#             "TotalPages" : total_pages,
#             "message" : "successful"
            
#             }

#     else :
#         data = []
#         for i in result:
#             data.append(i)
#             i.States
#             i.States.Countries
            
#         return  {
            
#             'Items' : data[start : end] , 
#             "Page" :  page_num , 
#             "PerPage" : page_size , 
#             "Totaldata" : result.count(),
#             "TotalPages" : int(total_pages + 1),
#             "message" : "successful"
            
#             }

#This request is for return one data from cities 
# @app.get('/cities/{id}/' , status_code=status.HTTP_200_OK)
# def by_id(  id : int ,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
#     new_blog = db.query(models.Cities).filter(models.Cities.id == id).first()
#     if not new_blog:
#         return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f'Data with this id {id} not found '},)
#     if new_blog.status == False :
#         return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f'Data with this id : {id} not found '},)

#     new_blog1 = []
#     new_blog1.append(new_blog)
#     return {
#             "Item" : new_blog1 , 
#             "message" : "Successful"
#             }



# This Cities API is updated API.
@app.get("/city/{S_id}/", status_code=status.HTTP_200_OK)
def city_get_all(S_id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    
    #validation for country 
    if S_id == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No State Available'},)
    check_country_id = db.query(models.States).get(S_id)
    if not check_country_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No State Available'},)
        

    result = db.query(models.Cities).filter(models.Cities.state_id ==  S_id)
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No State Available'},)
    print(result.count(), "##################")
    new_list = []
    for i in result:
        new_list.append(i)
        
    return  {
        
        'Items' : new_list, 
        "message"  : "Successful"
        
        }
    
    
# from PIL import Image
from fastapi import FastAPI, Form
from PIL import Image

@app.post('/businesses/' , status_code=status.HTTP_201_CREATED)
async def Businesses_function(    
    name :  Union[str , None] = Body(default=None) ,
    category_id :Union[int, str] = Body(default=None),
    parent_id :Union[int, str] = Body(default=None),
    sub_category_id : Union[int, str] = Body(default=None),
    country_id :Union[int, str] = Body(default=None),
    state_id : Union[int , str] = Body(default=None),
    city_id : Union[int , str] = Body(default= None),
    information :  Union[int , str] = Body(default= None),
    rating : Union[int , str] = Body(default= None),
    established_year : Union[Date, str] = Body(default=None),
    address :Union[str, None] = Body(default=None),
    logo_large : UploadFile = File(default= None)  ,
    logo_small : UploadFile = File(default= None),
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db), 
):
    

    print(
        type(name),name,"Name type \n",
        type(category_id),category_id,"category_id type \n",
        type(parent_id),parent_id,"parent_id type \n",
        type(sub_category_id),sub_category_id,"sub_category_id type \n",
        type(country_id),country_id,"country_id type \n",
        type(state_id),state_id,"state_id type \n",
        type(city_id),city_id,"city_id type \n",
        type(information),information,"information type \n",
        type(rating),rating,"rating type \n",
        type(established_year),established_year,"established_year type \n",
        type(address),address,"address type \n",
        print(rating , address)
        
    )

    if rating == "":
        rating = 0 
    if parent_id == "":
        parent_id = 'null'
    if information == "":
        information = 'null'
    
    # This validation is for file 
    # if logo_large == None:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Logo large field required'},)
        
    # if logo_small == None:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Logo small field required'},)
        
    try :
            
        with open("media/Logo_large/"+ logo_large.filename , 'wb') as image :
            shutil.copyfileobj(logo_large.file , image)
        # with open("media/"+ logo_small.filename , 'wb') as image :
        #     shutil.copyfileobj(logo_small.file , image)

        
        
        url_for_large_logo = str('media/Logo_large/' + logo_large.filename)
        
        print("+++++++++++++++++++")
        
        # url_for_small_logo = str('media/' + logo_small.filename)
        print(logo_large , "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        image = Image.open(f'media/Logo_large/{logo_large.filename}')
        new_image = image.resize((100, 100))
        new_image.save(f'media/Logo_small/{logo_large.filename}')
        
        
        
        url_for_small_logo = str('media/Logo_small/' + logo_large.filename)
    except:
        url_for_large_logo = 'null'
        url_for_small_logo = 'null'
        print()


    if name == '' or name == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Name field required'},)
    if category_id == '' or  category_id  == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Category field required'},)
    # if parent_id == '' or parent_id == None :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Parent_id field required'},)
    if sub_category_id == '' or sub_category_id == None  :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Sub_category field required'},)
    if country_id == '' or country_id == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Country field required'},)
    if state_id == '' or state_id == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Country field required'},)
    if city_id == '' or city_id == None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'City field required'},)
    # if information == '' or information == None :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'information field required'},)
    # if rating == '':
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Rating field required'},)
    if established_year == '' or established_year == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Established_year field required'},)
    
    if address == '' or address == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Address field required'},)
    
    
    
    category_id_is_disit_check = validation.digit_validation(category_id)
    if category_id_is_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Category id should be digit '},)
    
    # parent_id_is_disit_check = validation.digit_validation(parent_id)
    # if parent_id_is_disit_check == False :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'parent_ id should be digit '},)
        
    sub_category_id_disit_check =  validation.digit_validation(sub_category_id)
    if sub_category_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'sub_category_id id should be digit '},)
        
    country_id_disit_check = validation.digit_validation(country_id)
    if country_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'country_id id should be digit'},)
    
    state_id_disit_check = validation.digit_validation(state_id)
    if state_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'state_id id should be digit'},)
    
    
    city_id_disit_check =  validation.digit_validation(city_id) 
    if city_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'city_id id should be digit'},)
        

    
    
    
    
    data = sub_category_id 
    
    #validation 
    # check name is not null 
    print("2222222222222222222" , rating)
    check_name_validation =  validation.name_validation(name)
    if check_name_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Name field required'},)
    #check name should be gretterthan two character
    print("#####333333")
    check_length_validation = validation.length_validation(name)
    if check_length_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Length should be gretterthen 2 character'},)
    print("#####333333")
    
    # check Business category id is not 0 
    if category_id == 0 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Business_category with this id : {category_id} not found '},)
        
    # This validation is for check category id.    
    category_id_check = db.query(models.Business_categorys).filter(models.Business_categorys.id == category_id)
    if category_id_check.first() :
        if category_id_check.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category id with this id : {category_id} not found '},)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category id with this id : {category_id} not found '},)
    
    # This validation is for check parentid exist or not 
    # parent_id_check = db.query(models.Businesses).filter(models.Businesses.id == parent_id)
    # if parent_id_check.first() :
    #     if parent_id_check.first().status == False :
    #         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Parent  with this id : {category_id} not found '},)
    # else:
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Parent with this id : {category_id} not found '},)
    
    # This validation is for check subcategory exist or not and the status should be true 
    Business_sub_category_id_check = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == sub_category_id)
    if Business_sub_category_id_check.first() :
        if Business_sub_category_id_check.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_sub_category with this id : {sub_category_id} not found '},)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_sub_category with this id : {sub_category_id} not found '},)
    
    #This validation is for check country_id is exist or not if exist, the status should be true
    Country_id_check = db.query(models.Countries).filter(models.Countries.id == country_id)
    if Country_id_check.first() :
        if Country_id_check.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id :  {country_id} not found '},)
    
    
    # This validation is for check state_id is exist or not if exist the status should be true 
    state_id_check = db.query(models.States).filter(models.States.id == state_id)
    if state_id_check.first() :
        if state_id_check.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id :  {state_id} not found '},)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id :  {state_id} not found '},)
    
    

    
    # This validation is for check cityid is valid or not 
    city_id_check = db.query(models.Cities).filter(models.Cities.id == city_id)
    if city_id_check.first() :
        if city_id_check.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id :  {city_id} not found '},)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id :  {city_id} not found '},)
    
    
    # This validation is for check information can not be blank
    # information_validation_check = validation.name_validation(information)
    # if information_validation_check == True :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Information field required'},)

    # if len(str(information)) < 2 :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be greater-than 2 letter '},)
        
    
    # This validation is for address 
    address_validation_check = validation.name_validation(address)
    if address_validation_check == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Address field required '},)

    # address_validation_check_length  = validation.length_validation(address)
    # if address_validation_check_length == True:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretterthan 2 character'},)
            
    if established_year == None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Date time field required'},)


    print("##############")
    Business_post = models.Businesses(
        
        name = name ,
        category_id = category_id ,
        parent_id = parent_id,
        sub_category_id =data , 
        country_id = country_id ,
        state_id = state_id , 
        city_id = city_id, 
        logo_large = url_for_large_logo ,
        logo_small = url_for_small_logo,
        information =information,
        rating = rating,
        status = True ,
        established_year = established_year,
        address = address, 
        created_at= current_time , 
        updated_at= current_time       
                        
                                    )
    
    db.add(Business_post)
    db.commit()
    db.refresh(Business_post)
    
    Business_post1 = []
    Business_post1.append(Business_post)
    return  {
            "Item" : Business_post,
            "message" : "Successful"
            }


@app.put('/businesses/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Countries_update(
    id : int , 
    name :  Union[str , None] = Body(default=None) ,
    category_id :Union[int, str] = Body(default=None),
    parent_id :Union[int, str] = Body(default=None),
    sub_category_id : Union[int, str] = Body(default=None),
    country_id :Union[int, str] = Body(default=None),
    state_id : Union[int , str] = Body(default=None),
    city_id : Union[int , str] = Body(default= None),
    information : Union[str, None] = Body(default=None),
    rating : Union[int, str] = Body(default=None),
    address :Union[str, None] = Body(default=None),
    logo_large : UploadFile = File(default= None) ,
    logo_small : UploadFile = File(default= None),
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db), 
):
    
    
    
    # This validation is for file 
    # if logo_large == None:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Logo large field required'},)
        
    # if logo_small == None:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Logo small field required'},)
        
    try :
        
        with open("media/"+ logo_large.filename , 'wb') as image :
            shutil.copyfileobj(logo_large.file , image)
        with open("media/"+ logo_small.filename , 'wb') as image :
            shutil.copyfileobj(logo_small.file , image)

        url_for_large_logo = str('media/' + logo_large.filename)
        url_for_small_logo = str('media/' + logo_small.filename)

    except:
        url_for_large_logo = 'null'
        url_for_small_logo = 'null'
        print()

    if name == '' or name == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Name field required'},)
    if category_id == '' or  category_id  == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Category field required'},)
    # if parent_id == '' or parent_id == None :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Parent_id field required'},)
    if sub_category_id == '' or sub_category_id == None  :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Sub_category field required'},)
    if country_id == '' or country_id == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Country field required'},)
    if state_id == '' or state_id == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Country field required'},)
    if city_id == '' or city_id == None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'City field required'},)
    # if information == '' or information == None :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'information field required'},)
    # if rating == '':
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Rating field required'},)
    if address == '' or address == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Address field required'},)
    
    category_id_is_disit_check = validation.digit_validation(category_id)
    if category_id_is_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Category id should be digit '},)
    
    # parent_id_is_disit_check = validation.digit_validation(parent_id)
    # if parent_id_is_disit_check == False :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'parent_ id should be digit '},)
        
    sub_category_id_disit_check =  validation.digit_validation(sub_category_id)
    if sub_category_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'sub_category_id id should be digit '},)
        
    country_id_disit_check = validation.digit_validation(country_id)
    if country_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'country_id id should be digit'},)
    
    state_id_disit_check = validation.digit_validation(state_id)
    if state_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'state_id id should be digit'},)
    
    
    city_id_disit_check =  validation.digit_validation(city_id) 
    if city_id_disit_check == False :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'city_id id should be digit'},)
        


    if id == 0 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Id field required '},)
        
        
    fetch_data_business = db.query(models.Businesses).filter(models.Businesses.id == id )
    if not fetch_data_business.first():
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f'Data with this id {id} not found '},)

    else:
        
        
        if fetch_data_business.first().status == False:
            return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f'Data with this id {id} not found'},)







        check_name_validation =  validation.name_validation(name)
        if check_name_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Name field required ' },)
        #check name should be gretterthan two character
        check_length_validation = validation.length_validation(name)
        if check_length_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Length should be gretterthen 2 character'},)
        # check Business category id is not 0 
        if category_id == 0 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Business_category with this id :  {category_id} not found '},)
            
        # This validation is for check category id.    
        category_id_check = db.query(models.Business_categorys).filter(models.Business_categorys.id == category_id)
        if category_id_check.first() :
            if category_id_check.first().status == False :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category with this id : {category_id} not found '},)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_category with this id :  {category_id} not found '},)
        
        # This validation is for check parentid exist or not 
        
        
        # parent_id_check = db.query(models.Businesses).filter(models.Businesses.id == parent_id)
        # if parent_id_check.first() :
        #     if parent_id_check.first().status == False :
        #         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Parent with this id : {parent_id} not found '},)
        # else:
        #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Parent with this id : {parent_id} not found '},)
        
        # This validation is for check subcategory exist or not and the status should be true 
        Business_sub_category_id_check = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == sub_category_id)
        if Business_sub_category_id_check.first() :
            if Business_sub_category_id_check.first().status == False :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_sub_category with this id : {sub_category_id} not found '},)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_sub_category with this id : {sub_category_id} not found '},)
        
        #This validation is for check country_id is exist or not if exist, the status should be true
        Country_id_check = db.query(models.Countries).filter(models.Countries.id == country_id)
        if Country_id_check.first() :
            if Country_id_check.first().status == False :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
        
        
        # This validation is for check state_id is exist or not if exist the status should be true 
        state_id_check = db.query(models.States).filter(models.States.id == state_id)
        if state_id_check.first() :
            if state_id_check.first().status == False :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
        
        
        # This validation is for check cityid is valid or not 
        city_id_check = db.query(models.Cities).filter(models.Cities.id == city_id)
        if city_id_check.first() :
            if city_id_check.first().status == False :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
        
        
        # This validation is for check information can not be blank
        # information_validation_check = validation.name_validation(information)
        # if information_validation_check == True :
        #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Information field required '},)
            
        # This validation is for address 
        address_validation_check = validation.name_validation(address)
        if address_validation_check == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Address field required'},)

        # address_validation_check_length  = validation.length_validation(address)
        # if address_validation_check_length == True:
        #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretterthan 2 character'},)
            

        fetch_data_business = db.query(models.Businesses).filter(models.Businesses.id == id ).update(dict(name = name , category_id = category_id ,parent_id = parent_id ,sub_category_id = sub_category_id ,country_id = country_id , state_id = state_id ,city_id = city_id ,information = information,rating = rating,address = address,logo_large = url_for_large_logo , logo_small = url_for_small_logo,updated_at =  current_time ))
        db.commit()
        fetchdata = db.query(models.Businesses).filter(models.Businesses.id == id ).first()
        new = []
        new.append(fetchdata)

        
        return {
                    "Item" : new ,
                    "message" : "Successful"
            }
        


@app.get("/businesses/", status_code=status.HTTP_200_OK)
def Business_get_all(user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Businesses).filter(models.Businesses.status ==  True).order_by(models.Businesses.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business available'},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
            i.Category.name
            i.Sub_category
            i.Country
            i.States
            i.City

        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
            i.Category
            i.Sub_category
            i.Country
            i.States
            i.City

            
            
            
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "Successful" : "Successful"
            
            }



#This request is for return one data from businesses 
@app.get('/businesses/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Businesses).filter(models.Businesses.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)

    if new_blog.status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data not found with this id: {id}'},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
            "Item" : new_blog,
            "message" : "Successful"
            }

@app.delete('/businesses/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_state= db.query(models.Businesses).filter(models.Businesses.id == id)
    if not delete_data_state.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
    
    
    if delete_data_state.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
        
    
    delete_data_state = db.query(models.Businesses).filter(models.Businesses.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Detele Successfull"},)
    
    # return "Detele Successfull"






@app.post('/businessfaqs/' , status_code=status.HTTP_201_CREATED)
async def  Business_faqs_function(request : schema.business_faqs,user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), ):
    
    print(request.business_id)
    
    #validation of business id 
    check_business_id = validation.id_validation(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Business id can not be zero"},)
    
    # check business_id is exist or not in business table
    check = db.query(models.Businesses).filter(models.Businesses.id ==request.business_id ).first()
    if not check :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {request.business_id} is not found "},)
    if check.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {request.business_id} is not found "},)
        
    
    #validation for question field can not be null 
    question_validation = validation.name_validation(request.question)
    if question_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Question field can not be blank"},)
    question_length_validation = validation.length_validation(request.question)
    if question_length_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Length should be gretter than 2 character "},)
    
    
    #validation for answar field can not be blank 
    answar_validation = validation.name_validation(request.answar)
    if answar_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Answer field can not be blank "},)
    answer_length_validation = validation.length_validation(request.answar)
    if answer_length_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Length should be gretterthan 2 character "},)

    Business_faqs_post = models.Business_faqs(
    business_id = request.business_id ,
    question  = request.question , 
    answar = request.answar , 
    status  = True, 
    created_at = current_time , 
    updated_at = current_time ,
    )

    db.add(Business_faqs_post)
    db.commit()
    db.refresh(Business_faqs_post)
    Business_faqs_post1 = []
    Business_faqs_post1.append(Business_faqs_post)
    return {
            "Item" : Business_faqs_post1,
            "message" : "Successful"
            }



@app.put('/businessfaqs/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def category_update(id : int,  request : schema.business_faqs, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_category  = db.query(models.Business_faqs).filter(models.Business_faqs.id == id )
    print(fetch_data_category.exists())
    if not fetch_data_category.first():
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id{id} not found '},)
    if fetch_data_category.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id{id} not found '},)
        
    else:

    #validation of business id 
        check_business_id = validation.id_validation(request.business_id)
        if check_business_id == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"Data with this id : {id} not found"},)
        
        # check business_id is exist or not in business table
        check = db.query(models.Businesses).filter(models.Businesses.id ==request.business_id ).first()
        if not check :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {request.business_id} is not found "},)
        if check.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {request.business_id} is not found "},)
            
        
        #validation for question field can not be null 
        question_validation = validation.name_validation(request.question)
        if question_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Question field can not be blank"},)
        question_length_validation = validation.length_validation(request.question)
        if question_length_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Length should be gretter than 2 character "},)
        
        
        #validation for answar field can not be blank 
        answar_validation = validation.name_validation(request.answar)
        if answar_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Answer field can not be blank "},)
        answer_length_validation = validation.length_validation(request.answar)
        if answer_length_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Length should be gretterthan 2 character "},)

        
        fetch_data_category = db.query(models.Business_faqs).filter(models.Business_faqs.id == id ).update(dict(business_id = request.business_id ,question = request.question,updated_at =  current_time ))
        db.commit()
        print("/////////////////////////////")
        data =  db.query(models.Business_faqs).filter(models.Business_faqs.id == id ).first()
        
        data1  = []
        data1.append(data)
        return  {
                "Item" : data1,
                "message" : "Successful"
                }


@app.delete('/businessfaqs/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):    
    

    
    delete_data_Business_faqs = db.query(models.Business_faqs).filter(models.Business_faqs.id == id)
    if not delete_data_Business_faqs.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
    if delete_data_Business_faqs.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
        
    delete_data_Business_faqs = db.query(models.Business_faqs).filter(models.Business_faqs.id == id ).update(dict(status = False ))
    db.commit()
    # return "delete successful"
    return JSONResponse(content={"message":'Delete successful'},)


@app.get("/businessfaqs/", status_code=status.HTTP_200_OK)
def Business_get_all(user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) , page_num : int = 1 , page_size : int = 10):



    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_faqs).filter(models.Business_faqs.status ==  True).order_by(models.Business_faqs.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business_faqs found '},)

    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }    

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message"  : "Successful"

            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }



#This request is for return one data from businessfaqs 
@app.get('/businessfaqs/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_faqs).filter(models.Business_faqs.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)

    if new_blog.status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} already deleted '},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
        
    return {
            "Item" : new_blog1,
            "message" : "Successful"
            }






@app.post('/business_products/' , status_code=status.HTTP_201_CREATED)
async def Business_products_function(    
    business_id : Union[int, None] = Body(default=...),
    name : Union[str, None] = Body(default=...),
    descriptions : Union[str, None] = Body(default=...),
    file : UploadFile = File(...) ,
    price : Union[float, None] = Body(default= None),
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db), 
):
    with open("media/"+ file.filename , 'wb') as image :
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    

    Countries_post = models.Business_products(
        business_id = business_id ,
        name = name ,
        descriptions = descriptions ,
        image = url , 
        price = price , 
        status = True,
        created_at= current_time , 
        updated_at= current_time                       
                                    )
    

    # Validation for business id is not zero. 
    check_business_id = validation.id_check(business_id)
    if check_business_id == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Business id : {business_id} can not be zero'},)
    
    #Validation for business_id status 
    data = db.query(models.Businesses).filter(models.Businesses.id == business_id)
    if not data.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {business_id} not found '},)
    if data.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {business_id} not found '},)
        
    #Validation for name validatio 
    validation_name = validation.name_validation(name)
    if validation_name == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Name field is required'},)
    
    validation_name_length = validation.length_validation(name)
    if validation_name_length == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretter than 2 charecter '},)
        
    validation_name = validation.name_validation(descriptions)
    if validation_name == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Descriptions field is required'},)
    
    validation_name_length = validation.length_validation(descriptions)
    if validation_name_length == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretter than 2 charecter '},)
    # Validation is for price field is not null
    if price == None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Price field required"},)
        
    db.add(Countries_post)
    db.commit()
    db.refresh(Countries_post)
    
    Countries_post1 = []
    Countries_post1.append(Countries_post)
    return {
            "Item" : Countries_post1,
            "message" : "Successful"
            }




@app.put('/business_products/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Countries_update(
    id : int , 
    business_id : Union[int, None] = Body(default=...),
    name : Union[str, None] = Body(default=...),
    descriptions : Union[str, None] = Body(default=...),
    file : UploadFile = File(...) ,
    price : Union[float, None] = Body(default=...),
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db), 
):

    with open("media/"+ file.filename , 'wb') as image :
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    
    fetch_data_Business_products = db.query(models.Business_products).filter(models.Business_products.id == id )
    if not fetch_data_Business_products.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)

    if fetch_data_Business_products.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    else:
            
            

        # Validation for business id is not zero. 
        check_business_id = validation.id_check(business_id)
        if check_business_id == True:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f'Business id : {business_id} can not be zero'},)
        
        #Validation for business_id status 
        data = db.query(models.Businesses).filter(models.Businesses.id == business_id)
        if not data.first():
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {business_id} not found '},)
        if data.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {business_id} not found '},)
            
        #Validation for name validatio 
        validation_name = validation.name_validation(name)
        if validation_name == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Name field is required'},)
        
        validation_name_length = validation.length_validation(name)
        if validation_name_length == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretter than 2 charecter '},)
            
        validation_name = validation.name_validation(descriptions)
        if validation_name == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Descriptions field is required'},)
        
        validation_name_length = validation.length_validation(descriptions)
        if validation_name_length == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be gretter than 2 charecter '},)
        # Validation is for price field is not null
        if price == None :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"Price field required"},)
            
        
        fetch_data_Business_products = db.query(models.Business_products).filter(models.Business_products.id == id ).update(dict(business_id = business_id ,name = name , descriptions = descriptions ,image = url,price = price ,updated_at =  current_time ))
        db.commit()
        data = db.query(models.Business_products).filter(models.Business_products.id == id ).first()
        
        data1 = []
        data1.append(data)
        
        return  {
                "Item" : data1,
                "message" : "Successful"
                
                }



@app.delete('/business_products/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_Business_products= db.query(models.Business_products).filter(models.Business_products.id == id)
    if not delete_data_Business_products.first():
        
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)
    if delete_data_Business_products.first().status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)
        
    delete_data_Business_products = db.query(models.Business_products).filter(models.Business_products.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Delete successfull"},)


@app.get("/business_products/", status_code=status.HTTP_200_OK)
def Business_products_get_all(user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_products).filter(models.Business_products.status ==  True).order_by(models.Business_products.id.desc())
    
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": "No Business product available "},)
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }       

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "successful"
            
            }




#This request is for return one data from business_products 
@app.get('/business_products/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_products).filter(models.Business_products.id == id).first()
    if not new_blog:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id {id} not found"},)
        
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id {id} not found"},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
            "Item" :new_blog1,
            "message" : "Successful"
            }                                              




@app.post("/amenities_services/" , status_code=status.HTTP_201_CREATED)
def Amenities_services(request : schema.Amenities_services  ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    Amenities_services_post = models.Amenities_services(
        name = request.name ,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    
    #validation for name field 
    check_name_validation = validation.name_validation(request.name)
    if check_name_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Name Field required "},)
    
    check_length_validation = validation.length_validation(request.name)
    if check_length_validation  == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "Length should be gretterthan 2 character "},)
        
    check_data = db.query(models.Amenities_services).filter(models.Amenities_services.name == request.name)
    if check_data.first():
        if check_data.first().status == True :
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"Amenities {request.name} already exist"},)
            
        
    db.add(Amenities_services_post)
    db.commit()
    db.refresh(Amenities_services_post)
    
    Amenities_services_post1 = []
    Amenities_services_post1.append(Amenities_services_post)
    return {
            "Item" : Amenities_services_post1,
            "message" : "Successful"
            } 



@app.put('/amenities_services/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Amenities_services_update(id : int,  request : schema.Amenities_services,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    fetch_data_Amenities_services = db.query(models.Amenities_services).filter(models.Amenities_services.id == id )
    print(fetch_data_Amenities_services.exists())
    if not fetch_data_Amenities_services.first():
        
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)
        
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'blog with this id{id} not found ')
    if fetch_data_Amenities_services.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)

    check_data = db.query(models.Amenities_services).filter(models.Amenities_services.name == request.name)
    if check_data.first():
        if check_data.first().status == True :
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message": f"Amenities {request.name} already exist"},)
    


    #validation for name field
    check_name = validation.name_validation(request.name)
    if check_name == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message": "name field required"},)
        
    #     validation.name_validadtion1(request.name) # This validation is for name can not be blank 
    # validation.length_valiation1(request.name) # This validation is for length shold be greterthan 2 letter. 
    
    
    fetch_data_Amenities_services = db.query(models.Amenities_services).filter(models.Amenities_services.id == id ).update(dict(name = request.name ,updated_at =  current_time ))

    db.commit()
    data =  db.query(models.Amenities_services).filter(models.Amenities_services.id == id ).first()
    
    data1 = []
    data1.append(data)
    return  {
        "Item" : data1,
        "message" : "Successful"
        }
    
    
    
@app.delete('/amenities_services/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):    
    delete_data_Amenities_services = db.query(models.Amenities_services).filter(models.Amenities_services.id == id)
    if not delete_data_Amenities_services.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data with this id {id} not found '},)
    
    delete_data_Amenities_services = db.query(models.Amenities_services).filter(models.Amenities_services.id == id ).update(dict(status = False ))
    db.commit()
    # response.headers['delete_data'] = "data delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message" : "data delete successful"},)


@app.get('/amenities_services/', status_code=status.HTTP_200_OK)

def all_category(user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) , page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Amenities_services).filter(models.Amenities_services.status ==  True).order_by(models.Amenities_services.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : "No Amenities_services available"},)

    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }




#This request is for return one data from amenities_services 
@app.get('/amenities_services/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    new_blog = db.query(models.Amenities_services).filter(models.Amenities_services.id == id).first()
    
    if id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
    
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message" : "data delete successful"},)

    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} already deleted"},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
            "Item" :new_blog1,
            "message" : "Successful"
            }                                              




@app.post("/business_amenities_services/" , status_code=status.HTTP_201_CREATED)
def Business_amenities_services_post(request : schema.Business_amenities_services  , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    
    data = request.amenity_service_id
    data1 = data
    Business_amenities_services= models.Business_amenities_services(
        business_id = request.business_id ,
        amenity_service_id = data1,
        phone_number = request.phone_number ,
        status  = True, 
        created_at =current_time , 
        updated_at =current_time )
    
    
    # validation for business id  and amenity_service_id is not zero
    validate_businessid = validation.id_check(request.business_id)
    if validate_businessid == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : f"Business  with this id : {request.business_id} not found"},)
    validate_amenity_service_id = validation.id_check(request.amenity_service_id)
    if validate_amenity_service_id == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : f"Amenity_service with this id : {request.amenity_service_id} not found"},)
        
    # validation for business id exist or not and business id status false or true
    business_id_exist =  db.query(models.Businesses).filter(models.Businesses.id == request.business_id).first()
    if not business_id_exist:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Business  with this id : {request.business_id} not found"},)
    if business_id_exist.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Business  with this id : {request.business_id} not found"},)
        
    # validation for business amenity service
    
    amenity_service_exist = db.query(models.Amenities_services).filter(models.Amenities_services.id == request.amenity_service_id).first()
    if not amenity_service_exist:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Amenity service  with this id : {request.amenity_service_id} not found"},)
        
    if amenity_service_exist.status == False: 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Amenity service  with this id : {request.amenity_service_id} not found"},)
    
    amenity_service_exist1 = db.query(models.Amenities_services).filter(models.Amenities_services.id == request.amenity_service_id).first()
    
    # Validation for phone number 
    
    phone_num = request.phone_number
    if len(str(phone_num)) != 10 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : " Phone number length should be 10 digit "},)
        
    
    
    # validation.Business_faqs_validation(request.business_id , db)
    # validation.amenity_service_validation(request.amenity_service_id , db )
    # validation.Phonenumber_validation(request.phone_number)
    
    db.add(Business_amenities_services)
    db.commit()
    db.refresh(Business_amenities_services)
    Business_amenities_services1 = []
    
    Business_amenities_services1.append(Business_amenities_services)
    
    return  {
        
            "Item" :Business_amenities_services1,
            "message" : "Successful"
            
            }



@app.put('/business_amenities_services/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Business_amenities_services_updtae(id : int,  request : schema.Business_amenities_services,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    fetch_data_Business_amenities_services = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id )
    print(fetch_data_Business_amenities_services.exists())
    if not fetch_data_Business_amenities_services.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data  with this id : {id} not found '},)
        
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'blog with this id{id} not found ')
        
    else:
            
        # validation for business id  and amenity_service_id is not zero
        validate_businessid = validation.id_check(request.business_id)
        if validate_businessid == True:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : f"Business  with this id : {request.business_id} not found"},)
        validate_amenity_service_id = validation.id_check(request.amenity_service_id)
        if validate_amenity_service_id == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : f"Amenity_service with this id : {request.amenity_service_id} not found"},)
            
        # validation for business id exist or not and business id status false or true
        business_id_exist =  db.query(models.Businesses).filter(models.Businesses.id == request.business_id).first()
        if not business_id_exist:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Business  with this id : {request.business_id} not found"},)
        if business_id_exist.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Business  with this id : {request.business_id} not found"},)
            
        # validation for business amenity service
        
        amenity_service_exist = db.query(models.Amenities_services).filter(models.Amenities_services.id == request.amenity_service_id).first()
        if not amenity_service_exist:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Amenity service  with this id : {request.amenity_service_id} not found"},)
            
        if amenity_service_exist.status == False: 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Amenity service  with this id : {request.amenity_service_id} not found"},)
        
        
        # Validation for phone number 
        
        phone_num = request.phone_number
        if len(str(phone_num)) != 10 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : " Phone number length should be 10 digit "},)
            
    
        fetch_data_Business_amenities_services = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id ).update(dict(business_id = request.business_id ,amenity_service_id =  request.amenity_service_id , phone_number = request.phone_number , updated_at = current_time ))

        db.commit()
        data = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id ).first()
        
        data1 = []
        data1.append(data)
        return { 
                    "Item" : data1,
                    "message" : "Successful"
                    
                }
    
    

@app.delete('/business_amenities_services/{id}/', status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_Business_amenities_services = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id)
    if not delete_data_Business_amenities_services.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data with this id : {id} not found '},)
    if delete_data_Business_amenities_services.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data with this id : {id} not found '},)
        
    delete_data_Business_amenities_services = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id ).update(dict(status = False ))
    db.commit()
    # response.headers['delete_data'] = "data delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message" : "Data delete successful"},)
    


@app.get('/business_amenities_services/', status_code=status.HTTP_200_OK)
def all_category(user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) , page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.status ==  True).order_by(models.Business_amenities_services.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : "No business_amenities_services available"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
            i.Businesses
            i.Amenities_services
        return  {   
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful" 
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
            i.Businesses
            i.Amenities_services
            # i.Amenities_services
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }




#This request is for return one data from business_amenities_services 
@app.get('/business_amenities_services/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_amenities_services).filter(models.Business_amenities_services.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" :f'Data with this id {id} not found '},)

    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found"},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
        
            "Item" :new_blog1,
            "message" : "Successful"
            
            }                                             





@app.post("/payment_method/" , status_code=status.HTTP_201_CREATED)
def payment_method_post(request : schema.Payment_methods  ,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):
    payment_method= models.Payment_methods(
        name  = request.name ,
        status = True,
        created_at =current_time , 
        updated_at =current_time )
    
    # Validation for payment name can not be null 
    name_validate = validation.name_validation(request.name)
    if name_validate == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Name field is required "},)
    
    #Validation for length validation 
    length_validate =  validation.length_validation(request.name)  
    if length_validate == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Length should be greater-than 2 letter "},)
          
    
    # validation.name_validation1(request.name)
    # validation.length_validation1(request.name)
    
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    payment_method1 = []
    payment_method1.append(payment_method)
    
    return {
        
            "Item" :payment_method1,
            "message" : "Successful"
            
            }



@app.put('/payment_method/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def payment_method_updtae(id : int,  request : schema.Payment_methods,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_payment_method = db.query(models.Payment_methods).filter(models.Payment_methods.id == id )
    print(fetch_data_payment_method.exists())
    if not fetch_data_payment_method.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
    
    if fetch_data_payment_method.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
        
    
    else:
    # Validation for payment name can not be null 
        name_validate = validation.name_validation(request.name)
        if name_validate == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Name field is required "},)
        
        #Validation for length validation 
        length_validate =  validation.length_validation(request.name)  
        if length_validate == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Length should be greater-than 2 letter "},)
            
        fetch_data_payment_method = db.query(models.Payment_methods).filter(models.Payment_methods.id == id ).update(dict(name  = request.name  , updated_at = current_time ))
        db.commit()
        data = db.query(models.Payment_methods).filter(models.Payment_methods.id == id ).first()
        
        data1 = []
        data1.append(data)
        
        return {
            
                "Item" : data1,
                "message" : "Successful"
                
                }
    

@app.delete('/payment_method/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):    
    delete_data_payment = db.query(models.Payment_methods).filter(models.Payment_methods.id == id)
    if not delete_data_payment.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data with this id {id} not found '},)
    
    if delete_data_payment.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'Data with this id {id} not found '},)
        
    delete_data_payment = db.query(models.Payment_methods).filter(models.Payment_methods.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message" : "Delete successfull"},)
    
    # return "Delete successfull"


@app.get('/payment_method/', status_code=status.HTTP_200_OK)
def all_category( user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Payment_methods).filter(models.Payment_methods.status ==  True).order_by(models.Payment_methods.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : "No payment_method  available"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }



#This request is for return one data from payment_method 
@app.get('/payment_method/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Payment_methods).filter(models.Payment_methods.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'blog with this id {id} not found '},)
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f'blog with this id {id} not found '},)
        
    
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
            
            "Item" : new_blog1,
            "message"  : "Successful"
            
            }                                             




#user group
@app.post("/user_group/" , status_code=status.HTTP_201_CREATED)
def user_group_upload(request : schema.User_group  , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    payment_method= models.User_group_types(
        group_name  = request.group_name ,
        status = True,
        created_at =current_time , 
        updated_at =current_time )
    
    
    #Validation for group name
    group_validate = validation.name_validation(request.group_name)
    if group_validate == True:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Group field can not be blank "},)
    
    # validation for length 
    group_length = validation.length_validation(request.group_name)
    if group_length == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Length should be greater-than  2 letter "},)
            
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    
    payment_method1 = []
    payment_method1.append(payment_method) 
    
    return {
        
            "Item"  : payment_method1,
            "message" : "Successful"
            
            }




@app.put('/user_group/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def user_group_updtae(id : int,  request : schema.User_group, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    fetch_data_payment_method = db.query(models.User_group_types).filter(models.User_group_types.id == id )
    print(fetch_data_payment_method.exists())
    if not fetch_data_payment_method.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)

    if fetch_data_payment_method.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
        
    else:
            
        group_validate = validation.name_validation(request.group_name)
        if group_validate == True:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Group field can not be blank "},)
        
        # validation for length 
        group_length = validation.length_validation(request.group_name)
        if group_length == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" : "Length should be greater-than  2 letter "},)
                
        fetch_data_payment_method = db.query(models.User_group_types).filter(models.User_group_types.id == id ).update(dict(group_name  = request.group_name  , updated_at = current_time ))
        db.commit()
        data = db.query(models.User_group_types).filter(models.User_group_types.id == id ).first()
        
        data1 = []
        data1.append(data)
        return  {
            
                "Item" : data1,
                "message" : "Successful"
                
                }

@app.delete('/user_group/{id}/' , status_code=status.HTTP_200_OK)
def deleteuser(id ,response: Response,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db)):    
    delete_data_payment = db.query(models.User_group_types).filter(models.User_group_types.id == id)
    if not delete_data_payment.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" :f'Data with this id {id} not found '},)
    
    delete_data_payment = db.query(models.User_group_types).filter(models.User_group_types.id == id ).update(dict(status = False ))
    db.commit()
    # return "Delete successfull"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message" :"Delete successfull"},)

@app.get('/user_group/', status_code=status.HTTP_200_OK)
def all_category(  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):


    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.User_group_types).filter(models.User_group_types.status ==  True).order_by(models.User_group_types.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message" :"No user_group available "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }




#This request is for return one data from user_group 
@app.get('/user_group/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.User_group_types).filter(models.User_group_types.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" :f'Data with this id {id} not found '},)
    
    if new_blog.status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" :f'Data with this id {id} not found '},)
    
    
    new_blog1 = []
    new_blog1.append(new_blog) 
    return  {
        
                "Item" : new_blog1,
                "message" : "Successful"
                
                }                                             



# @app.post("/usertest")
# async def create_user(
#     username: str , 
#     password: SecretStr 
 
# ):
#     print(username)
#     print(password)



# @app.post("/user/" , status_code=status.HTTP_201_CREATED)
# async def user_upload(
#     f_name : str,
#     l_name : str , 
#     email : EmailStr ,
#     User_group : int,
#     password :SecretStr,
#     db : Session = Depends(get_db)

    
#     ):
#     print('$$$$$$$$$$$$$$$$$$$$$$$$$$$' , password)
#     payment_method= models.Users(
#         f_name  = f_name ,
#         l_name = l_name , 
#         email = email , 
#         User_group = User_group ,
#         password = password , 
#         status = True,
#         created_at =current_time , 
#         updated_at =current_time )
    
#     db.add(payment_method)
#     db.commit()
#     db.refresh(payment_method)
#     return payment_method




@app.put('/user/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
async def user_update(id : int,  request : schema.UserCreateschema1, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    fetch_data_payment_method = db.query(models.User).filter(models.User.id == id )
    print(fetch_data_payment_method.exists())
    if not fetch_data_payment_method.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {id} not found '},)
    if fetch_data_payment_method.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {id} not found '},)
        
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'blog with this id{id} not found ')
    else:
        fetch_data_payment_method = db.query(models.User).filter(models.User.id == id ).update(dict(f_name  = request.f_name,l_name = request.l_name, updateed_at = current_time ))
        db.commit()
        data = db.query(models.User).filter(models.User.id == id ).first()
        
        data1 = []
        data1.append(data)
        return  {
            
                "Item" : data1,
                "message" : "Successful"
                
                }
    


@app.delete('/user/{id}/' , status_code=status.HTTP_200_OK)
def user_delete(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_payment = db.query(models.User).filter(models.User.id == id)
    if not delete_data_payment.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    delete_data_payment = db.query(models.User).filter(models.User.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Delete successfull"},)

    # return "Delete successfull"



@app.get('/user/', status_code=status.HTTP_200_OK)
def all_category(  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.User).filter(models.User.status ==  True).order_by(models.User.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"No User available "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }




#This request is for return one data from user
@app.get('/user/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.User).filter(models.User.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            
            }                                             




# This api is get data by email 
@app.post('/email/' , status_code=status.HTTP_200_OK)
def get_by_email( request:schema.emailschema , db : Session = Depends(get_db)):
    new_blog = db.query(models.User).filter(models.User.email == request.email).first()
    # try :
    #     valid = _email_check.validate_email(email = request.email)
    #     email = valid.email
    # except _email_check.EmailNotValidError:
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"please enter a valid email "},)
        
    #     # raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
    # validation.email_validation(request.email , db)
    if not new_blog:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this email {request.email} not found '},)
        
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }                                             




import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm

from schema import UserCreate 
import services as _services
import schema as _schema

# @app.post("/api/users")
# async def create_user (user : _schema.UserCreate , db : _orm.Session = _fastapi.Depends(_services.get_db)):
#     db_user = await _services.get_user_by_email(email = user.email  , db = db )
#     if db_user:
#         raise _fastapi.HTTPException(
#             status_code= 400 , detail= "User with that email already exists"
#         )    
#     fname = user.f_name
#     l_name = user.l_name
#     password = user.password
#     conf_password = user.conf_password
#     user_group = user.user_group
    
#     validation.name_validation1(fname)
#     validation.length_validation1(fname)

#     validation.name_validation1(l_name)
#     validation.length_validation1(l_name)
#     validation.password_validation(password , conf_password)
#     validation.id_validation(user_group)
#     #return token 
#     return await _services.create_torken(user = user )





@app.post("/api/users/"  ,status_code=status.HTTP_202_ACCEPTED)
async def create_user (user : schema.UserCreate , db : _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(email = user.email  , db = db )
    if db_user:
        # raise _fastapi.HTTPException(
        #     # status_code= 400 , detail= "User with that email already exists")    
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":  "User with that email already exists"},)
    
    
    #create user
    
    user  = await _services.create_user(user = user , db = db )
    # This validation is for email vlaidation
    if user == "1":
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Email already exist'},)
    
    #This validation is for f_name can not be null
    if user == 'f_name_null':
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'F_name is Required '},)
    
    # This validation is for length should be gretter than 2 character 
    if user == "length_of_fname":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'F_name field Length should be greterthan 2 character'},)
    
    #This validation is for l_name canbe blank 


    #This validation is for password can not be null.
    if user == "password_null":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Password can not be Blank'},)
    if user == "password_error":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long.'},)

    #This validation is fopr user_group can not be null.
    if user ==  'user_group_zero':
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'User Group can not be Zero'},)
    # This validation is for user_group is exist or not in our db.
    if user == "user_group_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'User Group does not exist'},)
        
    #return token 
    return await _services.create_torken(user = user )



import datetime
@app.post("/api/token/",status_code=status.HTTP_202_ACCEPTED)
async def generate_token(
    form_data1 : schema.user_login,
    # form_data1  : _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db : _orm.Session = _fastapi.Depends(_services.get_db)):
    print(form_data1.username)

    # try :
        # valid = _email_check.validate_email(email = form_data1.username)
        # email = valid.email
    check_emial = db.query(models.User).filter(models.User.email == form_data1.username)
    if not  check_emial.first() :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Email not exist"},)
            
    print(form_data1.username)

    # except _email_check.EmailNotValidError:
    # except: 
    #     print("########################")
    #     pass
    #     # raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Email not exist"},)
    
    # check = validation.email_validation(form_data1.username , db)
    # if check == True :
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":  "Invalid Email"},)

    user = await _services.authenticate_user(email = form_data1.username , password= form_data1.password , db = db )
    
    if not user :
        # raise _fastapi.HTTPException(status_code=  401 , detail = "invalid Creadentials ")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Invalid Creadentials "},)
    
    db.query(models.User).update(dict(token_exp_time = datetime.datetime.now() + datetime.timedelta(days = config_data['Login_expire_time']['time']) ))
    db.commit()
    print(datetime.datetime.now() + datetime.timedelta(days = config_data['Login_expire_time']['time']))
    
    return await _services.create_torken(user = user)




#get current user 
# @app.get("/api/users/me" , response_model= _schema.User)
# async def get_user(user : _schema.User = _fastapi.Depends(_services.get_current_user)):
#     return user 


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# this is for password varification 
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#password change form after login 
@app.post('/passwordchange')
async def passchange(
    request : _schema.passchange ,
    user : _schema.User = _fastapi.Depends(_services.get_current_user),
    db : Session = Depends(get_db)):
    
    
    data = db.query(models.User).filter(models.User.email == user.email).first()
    if not verify_password(request.current_password, data.hashed_password):
        # raise _fastapi.HTTPException(status_code=404 , detail= "password not match")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Password not match"},)
    
    else:
        print("match")
        hashed_password1 = _hash.bcrypt.hash(request.new_password)
        
        db.query(models.User).filter(models.User.email == user.email ).update(dict(hashed_password = hashed_password1 ,updateed_at = current_time ))
        db.commit()

    # return "update_password"
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Update_password"},)


templates = Jinja2Templates(directory="templates")


# this is for email field 
    
    
    
    


@app.post("/forgot_password/" , status_code=status.HTTP_200_OK)
def read_item(request : schema.emailschema, db : Session = Depends(get_db)):

    try :
        valid = _email_check.validate_email(email =request.email)
        email = valid.email
    except _email_check.EmailNotValidError:
        # raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Please enter a valid email'},)
    
    data = db.query(models.User).filter(models.User.email == request.email).first()
    if data :
        print("email found successfully")
        port = 587  # For starttls
        code = str(uuid.uuid4()) 
        smtp_server = "smtp.gmail.com"
        sender_email = "hanishkaushal00@gmail.com"
        receiver_email = str(request.email)
        password = "ndqgzekzsgbkjqnd"
        SUBJECT = "varification mail"
        TEXT = f"http://localhost:4200/resetpassword?code={code}"
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)




        send_creadential = models.Otp_table(email = request.email , uuid = code)
        db.add(send_creadential)
        db.commit()
        db.refresh(send_creadential)
        try :
            
            db.query(models.Otp_table).filter(models.Otp_table.email == request.email ).update(dict(current_time  =  datetime.datetime.now() + datetime.timedelta(minutes=3)))
            db.commit()
        except :
            pass
        
        # return f"OTP send Successfully to this {receiver_email}"
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":f"OTP send Successfully to this {receiver_email}"},)
    
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Invalid Email'},)
        
        # return 'mail not found'
import datetime
import re
@app.post("/verification/", response_class=HTMLResponse)
async def read_item(request: Request ,form_schema : schema.passchange,  db : Session = Depends(get_db)):

    
    if form_schema.uuid == "":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'UUID is a Required feild '},)
    
    uuid_fetch =  db.query(models.Otp_table).filter(models.Otp_table.uuid == form_schema.uuid).first()
    if not uuid_fetch :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link Not found  '},)
    if uuid_fetch.uuid != form_schema.uuid:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link Not found  '},)
        
        
    time_validate = uuid_fetch.current_time
    print(time_validate)
    print(datetime.datetime.now())
    if datetime.datetime.now() > time_validate:
        print("time validate working fine %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link Expire'},)
        
    else:
        print("your link is not expire")
    if not uuid_fetch :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'UUID not match'},)
    if form_schema.new_password == "":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Password can not be blank'},)
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,50}$"
    pat = re.compile(reg)         
    mat = re.search(pat, form_schema.new_password)

    
    if mat:
        print("Password is valid.")
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long."},)
                
    if uuid_fetch.uuid == form_schema.uuid :
        user_email = uuid_fetch.email 
        hashed_password = _hash.bcrypt.hash(form_schema.new_password )
        db.query(models.User).filter(models.User.email == user_email ).update(dict(hashed_password = hashed_password))
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Password update successfully"},)

        
            

    
    # try :
    #     data = db.query(models.Otp_table).filter(models.Otp_table.uuid == form_schema.uuid).first()
    #     time = data.current_time 
    #     print(time , "1111111111111111111111111111")
    #     now = datetime.now()
    #     print(time , "2222222222222222222222222222222")
        
    #     diff_time = now - time
    #     print(time , "33333333333333333333333333333")
        
    #     print(type(config_data['forgot_password']['timelimit']) , "databasetime")
    #     if  diff_time  <  timedelta(minutes=config_data['forgot_password']['timelimit']) :

    #         print(time , "111111111111111111111464561111111")
            
    #         # validation 
    #         if form_schema.new_password == "":
    #             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Password can not be blank'},)

    #         # if len(form_schema.new_password) < 6 :
    #         #     return "Length should be 6"
    #         reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,50}$"
    #         pat = re.compile(reg)         
    #         mat = re.search(pat, form_schema.new_password)
    #         print(time , "1111111111111111111111111111112222")
            
    #         if mat:
    #             print("Password is valid.")
    #         else:
    #             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long."},)
                
    #             # return  "Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long."
    #         hashed_password = _hash.bcrypt.hash(form_schema.new_password )
    #         db.query(models.User).filter(models.User.email == data.email).update(dict(hashed_password = hashed_password ))

    #         db.commit() 
    #         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'You can Login now'},)

    #     else:
    #         a = 1
    #         # raise _fastapi.HTTPException(status_code=404 , detail= "Link expired ")
    #         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link expired'},)
               
    # except :
    #     if a == 1:
    #         # raise _fastapi.HTTPException(status_code=404 , detail= "Link expired ")
    #         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link expired'},)
        
            
    #     # raise _fastapi.HTTPException(status_code=404 , detail= "UUID not match")    
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'UUID not match'},)
        
        
        
        
# from fastapi.responses import RedirectResponse
# @app.get("/logout")

# def logout(response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
#     print(user.token)
#     response = RedirectResponse('/api/token/', status_code= 302)
#     # response.delete_cookie(key =token)
#     return response



# @app.post('/submitform/{email}/')
# async def validate(email , db : Session = Depends(get_db) ,password : str = Form(...) , conform_password : str = Form(...) ):
#     print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
#     print(email)
#     print(password)
#     print(conform_password)
    
#     if password == conform_password :
#         print(password)
#         print(conform_password)
#         hashed_password = _hash.bcrypt.hash(password)
#         db.query(models.User).filter(models.User.email == email).update(dict(hashed_password =hashed_password ))
#         db.commit()
#         return "password change successfully "
        
#     else:
#         return "password Does not match"
    
    
    
# check the otp is matched or not 

        
# @app.post('/after_otp_set_password/')
# async def set_password(
#     password : str , 
#     conf_password : str , 
#     db : Session = Depends(get_db)):
#         mail = read_item()
#         print(mail , " $$$$$$$$$$")
#         if len(password) < 4 :
#             raise _fastapi.HTTPException(status_code=404 , detail= "password should be gretter than 4charcter and number  ")
#         if password == conf_password:
#             hashed_password = _hash.bcrypt.hash(password)
#             db.query(models.User).update(dict(hashed_password =hashed_password  ))
#             db.commit()
#             return "password saved "
        
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= "password should be gretter than 5 charcter and number  ")
            



@app.post("/business_reaction/")
async def business_reactionn(request : schema.Business_reaction,user : _schema.User = _fastapi.Depends(_services.get_current_user) ,db : Session = Depends(get_db)):
    dict1 = {request.reaction_types_id : request.reaction_types_id }
    print('dsgdfnghjdfcjk')
    business_reactionn_post = models.Business_reaction(
        business_id = request.business_id ,
        reaction_types_id = dict1 ,
        user_id = request.user_id ,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )

    # validation for id check 
    if request.business_id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    check_business_id = db.query(models.Businesses).filter(models.Businesses.id == request.business_id ).first()
    if not check_business_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id}  not found '},)
        
    if check_business_id.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id}  not found '},)
    
    # Validation for business_reactiontype
    if request.reaction_types_id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id : {request.reaction_types_id} not found '},)
        
    reaction_types_id_check = db.query(models.Reaction_types).filter(models.Reaction_types.id ==request.reaction_types_id ).first()
    if not reaction_types_id_check :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id: {request.reaction_types_id}  not found '},)
    if reaction_types_id_check.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id: {request.reaction_types_id}  not found '},)
    
    
    
    #Validation for user 
    if request.user_id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
        
    userid_check = db.query(models.User).filter(models.User.id  == request.user_id ).first()
    if not userid_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
    if userid_check.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
        
    
    db.add(business_reactionn_post)
    db.commit()
    db.refresh(business_reactionn_post)
    
    business_reactionn_post1 = []
    business_reactionn_post1.append(business_reactionn_post)
    
    return  {
        
            "Item":business_reactionn_post1 ,
            "message" : "Successful"
            
            }



@app.get("/business_reaction/" , status_code=status.HTTP_200_OK)
async def business_reaction_get(user : _schema.User = _fastapi.Depends(_services.get_current_user)  ,db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_reaction).filter(models.Business_reaction.status ==  True).order_by(models.Business_reaction.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business_reaction available'},)
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }


@app.put('/business_reaction/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def category_update(id : int,  request : schema.Business_reaction , db : Session = Depends(get_db) ):
    fetch_data_Business_reaction = db.query(models.Business_reaction).filter(models.Business_reaction.id == id )
    print(fetch_data_Business_reaction.exists())
    if not fetch_data_Business_reaction.first(): 
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= f'blog with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found"})
    
    if fetch_data_Business_reaction.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found"})
        
        
    else:

        # validation for id check 
        if request.business_id == 0 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
        check_business_id = db.query(models.Businesses).filter(models.Businesses.id == request.business_id ).first()
        if not check_business_id:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id}  not found '},)
            
        if check_business_id.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id}  not found '},)
        
        # Validation for business_reactiontype
        if request.reaction_types_id == 0 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id : {request.reaction_types_id} not found '},)
            
        reaction_types_id_check = db.query(models.Reaction_types).filter(models.Reaction_types.id ==request.reaction_types_id ).first()
        if not reaction_types_id_check :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id: {request.reaction_types_id}  not found '},)
        if reaction_types_id_check.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Reaction_type with this id: {request.reaction_types_id}  not found '},)
        
        
        
        #Validation for user 
        if request.user_id == 0 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
            
        userid_check = db.query(models.User).filter(models.User.id  == request.user_id ).first()
        if not userid_check:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
        if userid_check.status == False :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id: {request.user_id}  not found '},)
        

        db.query(models.Business_reaction).filter(models.Business_reaction.id == id ).update(dict(business_id = request.business_id ,reaction_types_id = request.reaction_types_id,user_id = request.user_id,updated_at =  current_time ))
        db.commit()
        data =  db.query(models.Business_reaction).filter(models.Business_reaction.id == id ).first()
        data1 = []
        data1.append(data)
        
        return {
            
                "Item" : data1,
                "message" : "Successful"
                
                } 


@app.delete('/business_reaction/{id}', status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    delete_data_Business_reaction = db.query(models.Business_reaction).filter(models.Business_reaction.id == id)
    if not delete_data_Business_reaction.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " : f'Data with this id : {id} not found '},)
    
    # This validation is check for id status should be true 
    data = db.query(models.Business_reaction).filter(models.Business_reaction.id == id ).first()
    if data.status == False:
        # raise _fastapi.HTTPException(status_code=404 , detail= f"{id} already Deleted") 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} already Deleted"})
        
        
    delete_data_Business_reaction = db.query(models.Business_reaction).filter(models.Business_reaction.id == id ).update(dict(status = False ))
    db.commit()
    # return  "data delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message " :  "data delete successful"})

# get api by id 
@app.get('/business_reaction/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_reaction).filter(models.Business_reaction.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
        
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }                                              




# APi for User detail



# This Instance/API is  for countries
@app.post('/userdetail/',status_code=status.HTTP_201_CREATED)
async def Userdetail_function( user : _schema.User = _fastapi.Depends(_services.get_current_user),
    user_id : Union[int, None] = Body(default=...),
    city_id :Union[int, None] = Body(default=...), 
    state_id : Union[int, None] = Body(default=...), 
    country_id : Union[int, None] = Body(default=...), 
    pincode :Union[int, None] = Body(default=...), 
    date_of_birth : Union[Date, None] = Body(default=...), 
    gender :  Union[str, None] = Body(default=...), 
    mobile : Union[conint(gt=10), None] = Body(default=...), 
    file : UploadFile = File(...) ,

    db : Session = Depends(get_db), 
):
    user_id_check = db.query(models.User_detail).filter(models.User_detail.user_id == user_id).first()
    if  user_id_check :
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":f'User detail  already exist'},)
        
    # validation for user id 
    validate_userid = validation.id_check(user_id)
    if validate_userid == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {user_id} not found '},)

    # Validation for user_id exist or not and status should true
    check_exist = validation.user_exist_status_check(user_id , db)
    if check_exist == "user_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {user_id} not found '},)
        
    if check_exist == "user_id_status_false":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {user_id} not found '},)
        
    
    # Validation for city_id is not zero , should be exist in db and status True 
    
    check_city_id = validation.id_check(city_id)
    if check_city_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
    
    # Validation for city id exist or not and status should be true
    check_exist_city = validation.city_exist_status_check(city_id , db)
    if check_exist_city == "city_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
    if check_exist_city == "city_id_status_false":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
    
    
    # Validation for state 
    check_state_id = validation.id_check(state_id)
    if check_state_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
    
    # Validation for state id exist or not and status should be true
    check_state_exist = validation.state_exist_status_check(state_id , db)
    if check_state_exist == "state_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
    if check_state_exist == "state_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
        
    
    # validation for country id is not zero 
    check_country = validation.id_check(country_id)
    if check_country == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
    
    # Validation for country id should be exist and its status should be True 
    
    check_country_exist  = validation.country_exist_status_check(country_id,db )
    if check_country_exist == "country_id_not_exist" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
    if check_country_exist == "country_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
        
    
    #Validation for pin code 
    if  len(str(pincode)) < 3 or 7 < len(str(pincode)) :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Pincode length should be 3-7 '},)
    
    #validation for date_of_birth 
    if date_of_birth == None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'date_of_birth can not be blank '},)

    # Validation for gender 
    if gender == "":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Gender field can not be blank '},)
        
    #validation for mobile number 
    if not len(str(mobile)) == 10 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Mobile number should be 10 digit'},)
         
    
    
    
    
    
    
    
    with open("media/"+ file.filename , 'wb') as image :    
        shutil.copyfileobj(file.file , image)
    url = str('media/' + file.filename)
    
    User_detail_post = models.User_detail(
        
        user_id = user_id ,
        city_id = city_id ,
        state_id= state_id , 
        country_id = country_id , 
        pincode = pincode , 
        date_of_birth = date_of_birth , 
        gender = gender ,
        mobile = mobile ,
        image = url ,
        status = True ,
        created_at= current_time , 
        updated_at= current_time                       
                                    )
    
    
# try :
    
    db.add(User_detail_post)
    db.commit()
    db.refresh(User_detail_post)
    
    User_detail_post1 = []
    User_detail_post1.append(User_detail_post)
    return {
        
            "Item" :User_detail_post1,
            "message" : "Successful"
            
            }
    # except:
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'check relationship'},)



@app.put('/userdetail/{id}/',status_code=status.HTTP_202_ACCEPTED)
def Userdetail_update(
    id : int , 
    user : _schema.User = _fastapi.Depends(_services.get_current_user) , 
    city_id :Union[int, None] = Body(default=...), 
    state_id : Union[int, None] = Body(default=...), 
    country_id : Union[int, None] = Body(default=...), 
    pincode :Union[int, None] = Body(default=...), 
    date_of_birth : Union[Date, None] = Body(default=...), 
    gender :  Union[str, None] = Body(default=...), 
    mobile :  Union[conint(gt=10), None] = Body(default=...), 
    file : UploadFile = File(...) ,

    db : Session = Depends(get_db), 
):

    with open("media/"+ file.filename , 'wb') as image :
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    
    if id == 0 :
        # raise _fastapi.HTTPException(status_code=404 , detail= 'We can not proceed with 0')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'ID not found '},)
    
    fetch_data_userdetail = db.query(models.User_detail).filter(models.User_detail.id == id )
    if not fetch_data_userdetail.first():
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id{id} not found "},)

    else:
        
        # Validation for city_id is not zero , should be exist in db and status True 
        
        check_city_id = validation.id_check(city_id)
        if check_city_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
        
        # Validation for city id exist or not and status should be true
        check_exist_city = validation.city_exist_status_check(city_id , db)
        if check_exist_city == "city_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
        if check_exist_city == "city_id_status_false":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'City with this id : {city_id} not found '},)
        
        
        # Validation for state 
        check_state_id = validation.id_check(state_id)
        if check_state_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
        
        # Validation for state id exist or not and status should be true
        check_state_exist = validation.state_exist_status_check(state_id , db)
        if check_state_exist == "state_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
        if check_state_exist == "state_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'State with this id : {state_id} not found '},)
            
        
        # validation for country id is not zero 
        check_country = validation.id_check(country_id)
        if check_country == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
        
        # Validation for country id should be exist and its status should be True 
        
        check_country_exist  = validation.country_exist_status_check(country_id,db )
        if check_country_exist == "country_id_not_exist" :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
        if check_country_exist == "country_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Country with this id : {country_id} not found '},)
            
        
        #Validation for pin code 
        if not len(str(pincode)) > 3 and 7 < len(str(pincode)) :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Pincode length should be 3-7 '},)
        
        #validation for date_of_birth 
        if date_of_birth == None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'date_of_birth can not be blank '},)

        # Validation for gender 
        if gender == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Gender field can not be blank '},)
            
        #validation for mobile number 
        if not len(str(mobile)) == 10 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Mobile number should be 10 digit'},)            
        
        try :
                
            fetch_data_user_detail = db.query(models.User_detail).filter(models.User_detail.id == id ).update(dict(city_id = city_id ,state_id = state_id,country_id = country_id,pincode = pincode,date_of_birth = date_of_birth,gender = gender,mobile = mobile, image = url ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.User_detail).filter(models.User_detail.id == id ).first()

            data1 = []
            data1.append(data)
            
            return {
                
                    "Item" :data1 ,
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'check relationship'},)

@app.get('/userdetail/', status_code=status.HTTP_200_OK)
def all_Userdetail(  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), page_num : int = 1 , page_size : int = 10):
    # new_blog =  db.query(models.Countries).all()
    
    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.User_detail).filter(models.User_detail.status ==  True).order_by(models.User_detail.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'No Userdetail found'},)

    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }






@app.delete('/userdetail/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_Userdetail= db.query(models.User_detail).filter(models.User_detail.id == id)
    if not delete_data_Userdetail.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id {id} not found "},)
    
    delete_data_check = delete_data_Userdetail.first()
    if delete_data_check.status == False :
        
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= "Data already deleted")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} not found "},)
        
    db.query(models.User_detail).filter(models.User_detail.id == id ).update(dict(status = False))

    db.commit()
    # return "delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message": "Delete successful"},)




@app.get('/userdetail/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.User_detail).filter(models.User_detail.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }                                             






@app.post('/Business_rating/', status_code=status.HTTP_201_CREATED)
async def Business_category_function(request : schema.business_rating ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    print(request.rating , "222222222222222222")
    #Validation for business id .
    check_business_id = validation.id_check(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    
    
    #validation for user 
    
    user_validation = validation.id_check(request.user_id)
    if user_validation == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
         
    
    check_user_exist = validation.user_exist_status_check(request.user_id , db)
    if check_user_exist == "user_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
    if check_user_exist == "user_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
        

    

    Business_rating_post = models.Business_ratings(
        business_id = request.business_id ,
        user_id = request.user_id ,
        rating = request.rating  , 
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_rating_post)
    db.commit()
    db.refresh(Business_rating_post)
    
    Business_rating_post1 = []
    Business_rating_post1.append(Business_rating_post)
    
    return  {
            
            "Item" : Business_rating_post1,
            "message" : "Successful"
            
        }





@app.put("/Business_rating/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.business_rating, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Business_ratings).filter(models.Business_ratings.id == id ).first()
    if data and data.status == True : 
        # Validation for Business_id
        validate_business_id = validation.business_exist_status_check(request.business_id , db)
        if validate_business_id == "business_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        if validate_business_id == "business_id_status_false":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
        # Validation for user id 
        
        validate_user = validation.user_exist_status_check(request.user_id , db)  
        if validate_user == "user_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
        if validate_user == "user_id_status_false":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id :{request.user_id} not found '},)
        
        print(request.rating , "this is rating ")    
            
        
        try :
            
            db.query(models.Business_ratings).filter(models.Business_ratings.id == id ).update(dict(business_id = request.business_id  ,user_id =  request.user_id,rating = request.rating  ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Business_ratings).filter(models.Business_ratings.id == id ).first()
            data1 = []
            data1.append(data)
            
            return {
                
                    "Item" : data1 , 
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)
            

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)





# API for Business_rating delete
@app.delete('/Business_rating/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_category = db.query(models.Business_ratings).filter(models.Business_ratings.id == id)
    if not delete_data_category.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.business_rating_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_category = db.query(models.Business_ratings).filter(models.Business_ratings.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)




# API for Business_rating 
@app.get('/Business_rating/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user) , page_num : int = 1 , page_size : int = 10):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_ratings).filter(models.Business_ratings.status ==  True).order_by(models.Business_ratings.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"No Business_rating found"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message"  : "Successful"
            
            }





#API for Business rating get by id 
@app.get('/Business_rating/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Business_ratings).filter(models.Business_ratings.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.business_rating_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f" Id : {id} is already Deleted"},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }





# API for Business Review
@app.post('/Business_review/', status_code=status.HTTP_201_CREATED)
async def Business_category_function(request : schema.Business_reviews ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):

    #Validation for business id .
    check_business_id = validation.id_check(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    
    
    #validation for user 
    
    user_validation = validation.id_check(request.user_id)
    if user_validation == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
         
    
    check_user_exist = validation.user_exist_status_check(request.user_id , db)
    if check_user_exist == "user_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
    if check_user_exist == "user_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'User with this id : {request.user_id} not found '},)
        

    

    Business_review_post = models.Business_reviews(
        business_id = request.business_id ,
        user_id = request.user_id ,
        review = request.review  , 
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_review_post)
    db.commit()
    db.refresh(Business_review_post)
    
    Business_review_post1 = []
    Business_review_post1.append(Business_review_post)
    return  {
        
            "Item" :Business_review_post1,
            "message" : "Successful"
            
            }


# API for Business Review
@app.put("/Business_review/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.Business_reviews1, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Business_reviews).filter(models.Business_reviews.id == id ).first()
    if data and data.status == True : 
        # Validation for Business_id

        try :
            
            db.query(models.Business_reviews).filter(models.Business_reviews.id == id ).update(dict(review = request.review  ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Business_reviews).filter(models.Business_reviews.id == id ).first()
            data1 = []
            data1.append(data)
            return {
                
                
                "Item" : data1,
                "message" : "Successful"
                
                }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)
            

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)



# API for delete Business review
@app.delete('/Business_review/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_review = db.query(models.Business_reviews).filter(models.Business_reviews.id == id)
    if not delete_data_review.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.business_review_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_review = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)





# API for business review
@app.get('/Business_review/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Business_reviews).filter(models.Business_reviews.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.business_review_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
        
            "Item" : new_blog,
            "message" : "Successful"
            
            }



# API for Business_rating 
@app.get('/Business_review/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_reviews).filter(models.Business_reviews.status ==  True).order_by(models.Business_reviews.id.desc())
    if result.count == 0 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"No Business_review found "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }





#API for website link 



# API for Business Review
@app.post('/Website_link/', status_code=status.HTTP_201_CREATED)
async def Website_link_function(request : schema.Website_link ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):

    #Validation for business id .
    check_business_id = validation.id_check(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    
    
    #validation for link 
    
    if request.link =="":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Request link can not be blank '},)
        
    

    Website_post = models.Website_link(
        business_id = request.business_id ,
        link = request.link,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Website_post)
    db.commit()
    db.refresh(Website_post)
    
    Website_post1 = []
    Website_post1.append(Website_post)
    return {
        
            "Item" : Website_post,
            "message" : "Successful"
            
            }








# API for website link
@app.put("/Websitelink/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.Website_link, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Website_link).filter(models.Website_link.id == id ).first()
    if data and data.status == True : 
        # Validation for Business_id
    #Validation for business id .
        check_business_id = validation.id_check(request.business_id)
        if check_business_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
            
        check_business_id = validation.business_exist_status_check(request.business_id , db)
        if  check_business_id == "business_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
        if check_business_id == "business_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
            


        try :
            
            db.query(models.Website_link).filter(models.Website_link.id == id ).update(dict(business_id = request.business_id, link = request.link  ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Website_link).filter(models.Website_link.id == id ).first()
            data1 = []
            data1.append(data)
            return  {
                
                    "Item" :data1 ,
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)
            

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)




#API for website link get

@app.get('/Websitelink/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user) , page_num : int = 1 , page_size : int = 10):
        

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Website_link).filter(models.Website_link.status ==  True).order_by(models.Website_link.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Websitelink found '},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }



#API for websitelink delete 


@app.delete('/Websitelink/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_review = db.query(models.Website_link).filter(models.Website_link.id == id)
    if not delete_data_review.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.websitelink_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_review = db.query(models.Website_link).filter(models.Website_link.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)




@app.get('/Websitelink/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Website_link).filter(models.Website_link.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.websitelink_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog , 
            "message" : "Successful"
            
            }





# API is for Social media
@app.post('/Social_media/', status_code=status.HTTP_201_CREATED)
async def Social_media_function(request : schema.social_media ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    
    data = db.query(models.Social_media).filter(models.Social_media.name == request.name)
    if data.first():
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Same name already exist'},)
        
    #validation for name 
    if request.name =="":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":' Name field can not be blank '},)
        
    Socialmedia_post = models.Social_media(
        name  = request.name,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Socialmedia_post)
    db.commit()
    db.refresh(Socialmedia_post)
    Socialmedia_post1 = []
    Socialmedia_post1.append(Socialmedia_post)
    return {
        
            "Item" :Socialmedia_post1,
            "message" : "Successful"
            
            }



# API for website link
@app.put("/Social_media/{id}/",status_code=status.HTTP_202_ACCEPTED)
def Social_media_update(id : int,  request : schema.social_media, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Social_media).filter(models.Social_media.id == id ).first()
    if data and data.status == True : 
        if request.name == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Name field can not be blank '},)
        try :

            db.query(models.Social_media).filter(models.Social_media.id == id ).update(dict(name = request.name,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Website_link).filter(models.Website_link.id == id ).first()
            
            data1 = []
            data1.append(data)
            return {
                
                    "Item" : data1, 
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)



@app.get('/Social_media/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Social_media).filter(models.Social_media.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Social_media_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            }


@app.delete('/Social_media/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_social = db.query(models.Social_media).filter(models.Social_media.id == id)
    if not delete_data_social.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Social_media_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_social = db.query(models.Social_media).filter(models.Social_media.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)


@app.get('/Social_media/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Social_media).filter(models.Social_media.status ==  True).order_by(models.Social_media.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"No Social_media found "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages,
            "message" : 'Successful'
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : 'Successful'
            
            }








# API is for Business_social_website_links
@app.post('/Business_social_website_links/', status_code=status.HTTP_201_CREATED)
async def Business_social_website_linksfunction(request : schema.Business_social_website_links ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    #validation for check the link already exist or not.
    data = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.link == request.link)
    if data.first() :
         
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Same link already exist '},)
        
    
    check_business_id = validation.id_check(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    
    check_soical_meida = validation.id_check(request.social_media_id)
    if check_soical_meida == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'soical_meida with this id : {request.social_media_id} not found '},)

    check_social_id_exist = validation.social_exist_status_check(request.social_media_id , db )
    
    if check_social_id_exist == "data_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'soical_meida with this id : {request.social_media_id} not found '},)

    if check_social_id_exist == "data_already_delete":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'soical_meida with this id : {request.social_media_id} not found '},)
        
    
    if request.link == "":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link field is required'},)
    
    Business_social_website_links_post = models.Business_social_website_links(
        business_id  = request.business_id,
        social_media_id = request.social_media_id,
        link = request.link,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_social_website_links_post)
    db.commit()
    db.refresh(Business_social_website_links_post)
    
    Business_social_website_links_post1 = []
    Business_social_website_links_post1.append(Business_social_website_links_post)
    return {
        
            "Item" : Business_social_website_links_post1,
            "message" : "Successful"
            
            }



# This request is for Business_social_website_links put
@app.put("/Business_social_website_links/{id}/",status_code=status.HTTP_202_ACCEPTED)
def Social_media_update(id : int,  request : schema.Business_social_website_links1, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id ).first()
    if data and data.status == True : 

        if request.link == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Link field is required'},)
        
        #check the updated data is already exist or not 
        data1 = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.link == request.link)
        if data1.first():
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Link is already exist '},)
                    
        try :
            db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id ).update(dict(link = request.link,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id ).first()
            
            data1 = []
            data1.append(data)
            return  {
                
                    "Item" : data,
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)




@app.get('/Business_social_website_links/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.status ==  True).order_by(models.Business_social_website_links.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'No Business_social_website_links found'},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }





@app.delete('/Business_social_website_links/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_social = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id)
    if not delete_data_social.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Business_social_website_links_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_social = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)


@app.get('/Business_social_website_links/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Business_social_website_links_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }




    
# This Instance/API is  for Business_images
@app.post('/Business_images/',status_code=status.HTTP_201_CREATED)
async def Business_images_function( user : _schema.User = _fastapi.Depends(_services.get_current_user),
    business_id :  Union[int, None] = Body(default=...),
    file : UploadFile = File(...) ,
    db : Session = Depends(get_db), 
):
    
    # Validation for business_id
    validate_business_id = validation.id_check(business_id)
    if validate_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"business_id with this id : {business_id} not found "},)
    
    check_business_id = validation.business_exist_status_check(business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {business_id} not found '},)

    with open("media/"+ file.filename , 'wb') as image :    
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    print(url)
    # This validation is for check the image alredy exist or not 
    data = db.query(models.Business_images).filter(models.Business_images.image == url  )
    if data.first():
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Image already exists'},)

    Business_images = models.Business_images(
        
        business_id = business_id ,
        image = url ,
        status = True ,
        created_at= current_time , 
        updated_at= current_time                       
                                    )
    
    db.add(Business_images)
    db.commit()
    db.refresh(Business_images)
    
    Business_images1 = []
    Business_images1.append(Business_images)
    return {
        
            "Item" :Business_images1,
            "message" : "Successful"
            
            }





@app.put('/Business_images/{id}/',status_code=status.HTTP_202_ACCEPTED) 
def Business_images_update(
    id : int , 
    file : UploadFile = File(...) ,
    db : Session = Depends(get_db),  
):
    if id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_image with this id : {id} not found '},)
        
    # Validaion for check this id is already exist or not 
    data = db.query(models.Business_images).filter(models.Business_images.id == id) 
    if not data.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_image with this id : {id} not found '},)
        
    with open("media/"+ file.filename , 'wb') as image :
        shutil.copyfileobj(file.file , image)

    url = str('media/' + file.filename)
    
    db.query(models.Business_images).filter(models.Business_images.id == id ).update(dict(image = url ,updated_at =  current_time ))
    db.commit()
    data = db.query(models.Business_images).filter(models.Business_images.id == id ).first()

    data1 = []
    data1.append(data)
    return {
        
            "Item" : data1, 
            "message" : "Successful"
            
            }



@app.delete('/Business_images/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_Business_images= db.query(models.Business_images).filter(models.Business_images.id == id)
    if not delete_Business_images.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Business_image_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_Business_images = db.query(models.Business_images).filter(models.Business_images.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)





@app.get('/Business_images/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    new_blog = db.query(models.Business_images).filter(models.Business_images.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Businessimage_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }


@app.get('/Business_images/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_images).filter(models.Business_images.status ==  True).order_by(models.Business_images.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"No Business_images found "},)
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }

    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }

# This instance/ APi is for Business_working_hours  
@app.post('/Business_working_hours/', status_code=status.HTTP_201_CREATED)
async def state_function(request : schema.Business_working_hours, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db),):
     
     
    validate_business_id = validation.id_check(request.business_id)
    if validate_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"business_id with this id : {request.business_id} not found "},)
    
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)

    
    if request.open_time == 0.0:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Open time is a required field "},)
        
    if request.close_time == 0.0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Close time is a required field "},)

    print(request.business_id ,request.day_of_week ,request.open_time , request.close_time)
    state_post = models.Business_working_hours(
    business_id = request.business_id ,
    day_of_week = request.day_of_week ,
    open_time = request.open_time,
    close_time = request.close_time,
    created_at = current_time , 
    updated_at = current_time ,

    )

    db.add(state_post)
    db.commit()
    db.refresh(state_post)
    
    state_post1 = []
    state_post1.append(state_post)
    return {
        
            "Item" : state_post1,
            "message" : "Successful"
            
            }

    

@app.put("/Business_working_hours/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.Business_working_hours1, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):
    if id == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business_working_hours with this id : {id} not found '},)

    data = db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id )
    
    if  data.first()  :
        
        if request.day_of_week == 0 :
            
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Day_of_week is a required field "},)
        
        
        if request.open_time == 0.0 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Open time is a required field "},)

        if request.close_time == 0.0 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Close time is a required field "},)

        db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id ).update(dict(day_of_week = request.day_of_week  ,open_time =  request.open_time,close_time = request.close_time  ,updated_at =  current_time ))
        db.commit()
        data = db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id ).first()
        
        data1 = []
        data1.append(data)
        return {
            
                "Item" : data1,
                "message" : "Successful"
                
                }

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'2Business_working_hours with this id : {id} not found '},)





@app.get('/Business_working_hours/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    new_blog = db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id).first()
    
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }






@app.delete('/Business_working_hours/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_Business_images= db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id)
    if not delete_Business_images.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    delete_Business_images = db.query(models.Business_working_hours).filter(models.Business_working_hours.id == id ).delete()
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)










# API is for Tags
@app.post('/Tags/', status_code=status.HTTP_201_CREATED)
async def Tags_function(request : schema.Tags ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    
    data = db.query(models.Tags).filter(models.Tags.name == request.name)
    if data.first():
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Same name already exist'},)
        
    #validation for name 
    if request.name =="":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":' Name field required'},)
        
    Tags_post = models.Tags(
        name  = request.name,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Tags_post)
    db.commit()
    db.refresh(Tags_post)
    
    Tags_post1 = []
    Tags_post1.append(Tags_post)
    return {
        
        
            "Item" :Tags_post1,
            "message" : "Successful"
            
            }








@app.put("/Tags/{id}/",status_code=status.HTTP_202_ACCEPTED)
def Social_media_update(id : int,  request : schema.Tags, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Tags).filter(models.Tags.id == id ).first()
    if data and data.status == True : 
        if request.name == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Name field can not be blank '},)
        try :

            db.query(models.Tags).filter(models.Tags.id == id ).update(dict(name = request.name,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Tags).filter(models.Tags.id == id ).first()
            
            data1 = []
            data1.append(data)
            return {
                               
                    "Item" : data1,
                    "message" : "Successful"
                    
                }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)






@app.get('/Tags/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Tags).filter(models.Tags.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Tags_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog,
            "message" : "Successful"
            
        }


@app.delete('/Tags/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_social = db.query(models.Tags).filter(models.Tags.id == id)
    if not delete_data_social.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Tags_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_social = db.query(models.Tags).filter(models.Tags.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)






@app.get('/Tags/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Tags).filter(models.Tags.status ==  True).order_by(models.Tags.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"No Business_images found "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }
        





# This instance/ APi is for Business_working_hours  
@app.post('/Business_tags/', status_code=status.HTTP_201_CREATED)
async def state_function(request : schema.Business_tags, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db),):
     
     # Validation for Business id 
    validate_business_id = validation.id_check(request.business_id)
    if validate_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"business_id with this id : {request.business_id} not found "},)
    
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)

    
    # Validation for Tags id 
    tag_id_check = validation.id_check(request.tag_id)
    if tag_id_check == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
    
    check_tag_id_status = validation.tag_id_status_check(request.tag_id , db )
    if check_tag_id_status == "Tags_id_not_found":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
    if check_tag_id_status == "tags_status_false":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
    
    
    if request.phone_number == None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Phone numbr field is required"},)
        
    if len(str(request.phone_number)) != 10 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Phone number should be 10 digit "},)
        
    
    Business_tags_post = models.Business_tags(
    business_id = request.business_id ,
    tag_id = request.tag_id ,
    phone_number = request.phone_number,
    status  = True,
    created_at = current_time , 
    updated_at = current_time ,

    )

    db.add(Business_tags_post)
    db.commit()
    db.refresh(Business_tags_post)
    Business_tags_post1 = []
    Business_tags_post1.append(Business_tags_post)
    return {
        
            "Item" : Business_tags_post1,
            "message" : "Successful"
            }





@app.put('/Business_tags/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def Business_tags_updtae(id : int,  request : schema.Business_tags,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_Business_tags = db.query(models.Business_tags).filter(models.Business_tags.id == id )
    print(fetch_data_Business_tags.exists())
    if not fetch_data_Business_tags.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
    
    if fetch_data_Business_tags.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
        
    
    else:
        validate_business_id = validation.id_check(request.business_id)
        if validate_business_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"business_id with this id : {request.business_id} not found "},)
        
        check_business_id = validation.business_exist_status_check(request.business_id , db)
        if  check_business_id == "business_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
        if check_business_id == "business_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)

        
        # Validation for Tags id 
        tag_id_check = validation.id_check(request.tag_id)
        if tag_id_check == True:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
        
        check_tag_id_status = validation.tag_id_status_check(request.tag_id , db )
        if check_tag_id_status == "Tags_id_not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
        if check_tag_id_status == "tags_status_false":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Tag  with this id : {request.tag_id} not found "},)
        
        
        if request.phone_number == None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Phone numbr field is required"},)
            
        if len(str(request.phone_number)) != 10 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Phone number should be 10 digit "},)
            

        fetch_data_Business_tags = db.query(models.Business_tags).filter(models.Business_tags.id == id ).update(dict(business_id  = request.business_id,tag_id = request.tag_id , phone_number = request.phone_number  , updated_at = current_time ))
        db.commit()
        data = db.query(models.Business_tags).filter(models.Business_tags.id == id ).first()
        
        data1 = []
        data1.append(data)
        
        return {
            
                "Item" : data1,
                "message" : "Successful"
                
                }



@app.delete('/Business_tags/{id}', status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    delete_data_Business_tags= db.query(models.Business_tags).filter(models.Business_tags.id == id)
    if not delete_data_Business_tags.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " : f'Data with this id : {id} not found '},)
    
    # This validation is check for id status should be true 
    data = db.query(models.Business_tags).filter(models.Business_tags.id == id ).first()
    if data.status == False:
        # raise _fastapi.HTTPException(status_code=404 , detail= f"{id} already Deleted") 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"Data with this id : {id} already Deleted"})
        
        
    delete_data_Business_tags = db.query(models.Business_tags).filter(models.Business_tags.id == id ).update(dict(status = False ))
    db.commit()
    # return  "data delete successful"
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message " :  "Data delete successful"})





# API for Business_rating 
@app.get('/Business_tags/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_tags).filter(models.Business_tags.status ==  True).order_by(models.Business_tags.id.desc())
    if result.count == 0 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"No Business_review found "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            }

@app.get('/Business_tags/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    # Check id is exist or not in db.
    new_blog = db.query(models.Business_tags).filter(models.Business_tags.id == id).first()
    if not new_blog:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " :  f'Data with this id {id} not found'},)
    
    # Validation is for check the data is already deleted or not.
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message " :  f'Data already deleted with this id : {id}'},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
            "Item" : new_blog1,
            "message" : "Successful"
            } 





@app.post('/Business_Professionals/' , status_code=status.HTTP_201_CREATED)
async def  Business_Professionals(request : schema.Business_Professionals,user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db), ):
    
    # Validation for name 
    name_validation = validation.name_validation(request.name)
    if name_validation == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Name field required"},)
    
    name_length_validation = validation.length_validation(request.name)
    if name_length_validation == True:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-then 2 character"},)
        
    
    # Validation for business_id check 
    business_id_check = validation.id_check(request.business_id)
    if business_id_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id}not found "},)
        
    business_id_status_check = validation.business_exist_status_check(request.business_id , db )
    if business_id_status_check == "business_id_not_exist" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id}not found "},)
    if business_id_status_check == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id}not found "},)
        
    # Validation for designtion 
    
    designtion_check = validation.name_validation(request.designtion)
    if designtion_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Designtion field required"},)
    
    designation_length_check = validation.length_validation(request.designtion)
    if designation_length_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":" Length should be greater-than 2 character"},)
        
    # Validation for speciality 
    
    speciality_check = validation.name_validation(request.speciality)
    if speciality_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Speciality field required "},)
        
    speciality_length_check = validation.length_validation(request.speciality)
    if speciality_length_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-then 2 character"},)
        
    
    
    #Validation for qualification 

    qualification_check = validation.name_validation(request.qualification)
    if qualification_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Qualification field required"},)
        
    qualification_length_check = validation.length_validation(request.qualification)
    if qualification_length_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-than 2 character"},)
    
    
    try :
        valid = _email_check.validate_email(email =request.email)
        email = valid.email
    except _email_check.EmailNotValidError:
        # raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Please enter a valid email'},)
    
    
    #Validation for mobile number 
    if len(str(request.phone_number)) != 10 :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Mobile number should be 10 digit '},)

    #Validation for address 
    
    address_validation = validation.name_validation(request.address)
    if address_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Address field required'},)
        
    address_length_validation = validation.length_validation(request.address)
    if address_length_validation == True :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be greater-then 2 character'},)



    Business_Professionals_post = models.Business_Professionals(
    name = request.name,
    business_id = request.business_id ,
    designtion = request.designtion,
    speciality = request.speciality,
    qualification = request.qualification,
    email = request.email,
    phone_number = request.phone_number,
    address = request.address,
    status  = True, 
    created_at = current_time , 
    updated_at = current_time ,
    )

    db.add(Business_Professionals_post)
    db.commit()
    db.refresh(Business_Professionals_post)
    
    Business_Professionals_post1 = []
    
    Business_Professionals_post1.append(Business_Professionals_post)
    
    return {
            "Item" : Business_Professionals_post1,
            "message" : "Successful"
            }







@app.get('/Business_Professionals/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_Professionals).filter(models.Business_Professionals.status ==  True).order_by(models.Business_Professionals.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"No Business_images found "},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }
        





@app.put('/Business_Professionals/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def Business_Professionals_update(id : int,  request : schema.Business_Professionals, user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_category  = db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id )
    print(fetch_data_category.exists())
    if not fetch_data_category.first():
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id{id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    if fetch_data_category.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    else:
        
        # Validation for name 
        name_validation = validation.name_validation(request.name)
        if name_validation == True:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Name field required"},)
        
        name_length_validation = validation.length_validation(request.name)
        if name_length_validation == True:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-then 2 character"},)
            
        
        # Validation for business_id check 
        business_id_check = validation.id_check(request.business_id)
        if business_id_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id} not found "},)
            
        business_id_status_check = validation.business_exist_status_check(request.business_id , db )
        if business_id_status_check == "business_id_not_exist" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id} not found "},)
        if business_id_status_check == "business_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Business with this id : {request.business_id} not found "},)
            
        # Validation for designtion 
        
        designtion_check = validation.name_validation(request.designtion)
        if designtion_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Designtion field required"},)
        
        designation_length_check = validation.length_validation(request.designtion)
        if designation_length_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":" Length should be greater-than 2 character"},)
            
        # Validation for speciality 
        
        speciality_check = validation.name_validation(request.speciality)
        if speciality_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Speciality field required "},)
            
        speciality_length_check = validation.length_validation(request.speciality)
        if speciality_length_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-then 2 character"},)
            
        
        
        #Validation for qualification 

        qualification_check = validation.name_validation(request.qualification)
        if qualification_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Qualification field required"},)
            
        qualification_length_check = validation.length_validation(request.qualification)
        if qualification_length_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Length should be greater-than 2 character"},)
        
        
        try :
            valid = _email_check.validate_email(email =request.email)
            email = valid.email
        except _email_check.EmailNotValidError:
            # raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Please enter a valid email'},)
        
        
        #Validation for mobile number 
        if len(str(request.phone_number)) != 10 :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Mobile number should be 10 digit '},)

        #Validation for address 
        
        address_validation = validation.name_validation(request.address)
        if address_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Address field required'},)
            
        address_length_validation = validation.length_validation(request.address)
        if address_length_validation == True :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":'Length should be greater-then 2 character'},)


        
        fetch_data_category = db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id ).update(dict(name = request.name,business_id = request.business_id,designtion = request.designtion,speciality = request.speciality,qualification = request.qualification, email = request.email, phone_number = request.phone_number, address = request.address ,updated_at =  current_time ))
        db.commit()

        data =  db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id ).first()
        
        data1 = []
        data1.append(data)
        
        return  {
                "Item" : data1,
                "message" : "Successful"
                }





@app.delete('/Business_Professionals/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_state= db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id)
    if not delete_data_state.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
    
    
    if delete_data_state.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
        
    
    delete_data_state = db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Detele Successfull"},)
    
    # return "Detele Successfull"





# get api by id 
@app.get('/Business_Professionals/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_Professionals).filter(models.Business_Professionals.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }                                              







# API is for Business_social_website_links
@app.post('/Business_phone_numbers/', status_code=status.HTTP_201_CREATED)
async def Business_Professionals_function(request : schema.Business_phone_numbers ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    # validation for check the link already exist or not.
    data = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.number == request.number)
    if data.first() :
         
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Same number already exist '},)
    check_business_id = validation.id_check(request.business_id)
    
    
    # Validation for business_id 
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    # Valiadation for phone_type
    if request.phone_type == "" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Phone_type fileld  required '},)

    
    #Validation for 
    if request.phone_type == "mobile":
        if len(str(request.number)) != 10 :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Number should be greater than 10 digit '},)

    if request.phone_type == "land-line":
        if len(str(request.number)) != 5:
            print(len(str(request.phone_type)))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'land-line should be greater than 5 digit '},)
            
        
    if request.description == "":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Description field is required'},)
    
    length_check = validation.length_validation(request.description)
    if length_check == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Length should be greater-than 2 letters'},)
        
    
    if request.is_primary == None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Is primary field required '},)
        
    
    Business_phone_numbers_post = models.Business_phone_numbers(
        business_id  = request.business_id,
        phone_type = request.phone_type,
        number = request.number,
        description = request.description,
        is_primary = request.is_primary,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_phone_numbers_post)
    db.commit()
    db.refresh(Business_phone_numbers_post)
    Business_phone_numbers_post1 = []
    Business_phone_numbers_post1.append(Business_phone_numbers_post)
    
    return {
        
            "Item" : Business_phone_numbers_post1,
            "message" : "Successful"
            
            }






@app.put('/Business_phone_numbers/{id}/' ,status_code=status.HTTP_202_ACCEPTED)
def Business_phone_numbers_updtae(id : int,  request : schema.Business_phone_numbers,  user : _schema.User = _fastapi.Depends(_services.get_current_user),db : Session = Depends(get_db) ):
    fetch_data_Business_tags = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.id == id )
    print(fetch_data_Business_tags.exists())
    if not fetch_data_Business_tags.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
    
    if fetch_data_Business_tags.first().status == False:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message" : f"Data with this id : {id} not found "},)
        
    
    else:
        data = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.number == request.number)
        if data.first() :
            
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,content={"message":'Same number already exist '},)
        check_business_id = validation.id_check(request.business_id)
        
        
        # Validation for business_id 
        if check_business_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
            
        check_business_id = validation.business_exist_status_check(request.business_id , db)
        if  check_business_id == "business_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
        if check_business_id == "business_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
            
        
        # Valiadation for phone_type
        if request.phone_type == "" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Phone_type fileld  required '},)

        
        #Validation for 
        if request.phone_type == "mobile":
            if len(str(request.number)) != 10 :
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Number should be greater than 10 digit '},)

        if request.phone_type == "land-line":
            if len(str(request.number)) != 5:
                print(len(str(request.phone_type)))
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'land-line should be greater than 5 digit '},)
                
            
        if request.description == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Description field is required'},)
        
        length_check = validation.length_validation(request.description)
        if length_check == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Length should be greater-than 2 letters'},)
            
        
        if request.is_primary == None:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Is primary field required '},)
        fetch_data_Business_tags = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.id == id ).update(dict(business_id  = request.business_id,phone_type = request.phone_type , number = request.number  , updated_at = current_time ))
        db.commit()
        data = db.query(models.Business_tags).filter(models.Business_tags.id == id ).first()
        
        data1 = []
        data1.append(data)
        return {
            
                "Item" : data1,
                "message" : "Successful"
                
                }




# get api by id 
@app.get('/Business_phone_numbers/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int , user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    new_blog = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.id == id).first()
    if not new_blog:
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
    
    if new_blog.status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)
        
    new_blog1 = []
    new_blog1.append(new_blog)
    
    return {
        
        
            "Item" : new_blog,
            "message" : "Successful"
            
            }                                              



@app.delete('/Business_phone_numbers/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):    
    delete_data_state= db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.id == id)
    if not delete_data_state.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
    
    
    if delete_data_state.first().status == False :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id {id} not found '},)
        
    
    delete_data_state = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.id == id ).update(dict(status = False))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"Detele Successfull"},)
    
    # return "Detele Successfull"





@app.get('/Business_phone_numbers/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_phone_numbers).filter(models.Business_phone_numbers.status ==  True).order_by(models.Business_phone_numbers.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"No Business number found"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }
    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }
        








#API for Reaction_types
@app.post('/Reaction_types/', status_code=status.HTTP_201_CREATED)
async def Tags_function(request : schema.Reaction_types ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):
    

    #validation for name 
    if request.type =="":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":' Name field required'},)
        
    Reaction_types_post = models.Reaction_types(
        type  = request.type,
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Reaction_types_post)
    db.commit()
    db.refresh(Reaction_types_post)
    
    Reaction_types_post1 = []
    Reaction_types_post1.append(Reaction_types_post)
    return {
        
        
            "Item" :Reaction_types_post1,
            "message" : "Successful"
            
            }
    



@app.put("/Reaction_types/{id}/",status_code=status.HTTP_202_ACCEPTED)
def Social_media_update(id : int,  request : schema.Reaction_types, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Reaction_types).filter(models.Reaction_types.id == id ).first()
    if data and data.status == True : 
        if request.type == "":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'type field can not be blank '},)
        try :

            db.query(models.Reaction_types).filter(models.Reaction_types.id == id ).update(dict(type = request.type,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Reaction_types).filter(models.Reaction_types.id == id ).first()
            
            data1 = []
            data1.append(data)
            return {
                               
                    "Item" : data1,
                    "message" : "Successful"
                    
                }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)





@app.get('/Reaction_types/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Reaction_types).filter(models.Reaction_types.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Reaction_type_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"data with this id {id} not found "},)
    
    new_blog1 = []
    new_blog1.append(new_blog)
    return {
        
            "Item" : new_blog1,
            "message" : "Successful"
            
        }





@app.delete('/Reaction_types/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_social = db.query(models.Reaction_types).filter(models.Reaction_types.id == id)
    if not delete_data_social.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Reaction_type_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_social = db.query(models.Reaction_types).filter(models.Reaction_types.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)



@app.get('/Reaction_types/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user), page_num : int = 1 , page_size : int = 10 ):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Reaction_types).filter(models.Reaction_types.status ==  True).order_by(models.Reaction_types.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Reaction_types Not found"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }
    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message" : "Successful"
            
            }
        










@app.post('/Business_accepted_payment_methods/', status_code=status.HTTP_201_CREATED)
async def Business_accepted_payment_methods_function(request : schema.Business_method_payment_id ,user : _schema.User = _fastapi.Depends(_services.get_current_user) , db : Session = Depends(get_db)   ):

    #Validation for business id .
    check_business_id = validation.id_check(request.business_id)
    if check_business_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    check_business_id = validation.business_exist_status_check(request.business_id , db)
    if  check_business_id == "business_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
    
    if check_business_id == "business_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        
    
    
    #Validation for paymentid
    
    check_payment_id = validation.id_check(request.payment_method_id)
    if check_payment_id == True :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
        
    check_business_id_status = validation.payment_exist_status_check(request.payment_method_id , db)
    if  check_business_id_status == "payment_id_not_exist":
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
    
    if check_business_id_status == "payment_id_status_false" : 
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
        
    Business_accepted_payment_methods_post = models.Business_accepted_payment_methods(
        business_id = request.business_id ,
        payment_method_id = request.payment_method_id , 
        status  = True, 
        created_at = current_time , 
        updated_at = current_time )
    
    db.add(Business_accepted_payment_methods_post)
    db.commit()
    db.refresh(Business_accepted_payment_methods_post)
    
    Business_accepted_payment_methods_post1 = []
    Business_accepted_payment_methods_post1.append(Business_accepted_payment_methods_post)
    
    return  {
            
            "Item" : Business_accepted_payment_methods_post1,
            "message" : "Successful"
            
        }







@app.put("/Business_accepted_payment_methods/{id}/",status_code=status.HTTP_202_ACCEPTED)
def state_update(id : int,  request : schema.Business_method_payment_id, user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db) ):

    data = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id ).first()
    if data and data.status == True : 
        # Validation for Business_id
        validate_business_id = validation.business_exist_status_check(request.business_id , db)
        if validate_business_id == "business_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        if validate_business_id == "business_id_status_false":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Business with this id : {request.business_id} not found '},)
        

        #Validation for paymentid
        
        check_payment_id = validation.id_check(request.payment_method_id)
        if check_payment_id == True :
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
            
        check_business_id_status = validation.payment_exist_status_check(request.payment_method_id , db)
        if  check_business_id_status == "payment_id_not_exist":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
        
        if check_business_id_status == "payment_id_status_false" : 
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Payment with this id : {request.payment_method_id} not found '},)
        try :
            
            db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id ).update(dict(business_id = request.business_id  ,payment_method_id =  request.payment_method_id  ,updated_at =  current_time ))
            db.commit()
            data = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id ).first()
            
            data1 = []
            data1.append(data)
            return {
                
                    "Item" : data1 , 
                    "message" : "Successful"
                    
                    }
        except:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Relation ship error'},)
            

    else:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f'Data with this id : {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f'Data with this id : {id} not found '},)






# API for Business_rating delete
@app.delete('/Business_accepted_payment_methods/{id}/' , status_code=status.HTTP_200_OK)
def deleteblog(id ,response: Response ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):
    
        
    delete_data_Business_accepted_payment_method = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id)
    if not delete_data_Business_accepted_payment_method.first():
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id {id} not found '},)
    
    
    check = validation.Business_accepted_payment_methods_deletecheck (id , db)
    if check == "data_already_delete" :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":f"Data with this id : {id} not found "},)

    delete_data_Business_accepted_payment_method = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id ).update(dict(status = False ))
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"delete successfully"},)







@app.get('/Business_accepted_payment_methods/' , status_code=status.HTTP_200_OK)
def fetch_data( db : Session = Depends(get_db) , user : _schema.User = _fastapi.Depends(_services.get_current_user) , page_num : int = 1 , page_size : int = 10):
    

    start = (page_num -1) * page_size
    end = start + page_size    
    result = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.status ==  True).order_by(models.Business_accepted_payment_methods.id.desc())
    if result.count() == 0 :
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"No Business_accepted_payment_methods found"},)
        
    if page_num < 0 or page_size < 0 :
        
        return  {
            
            'Items' : list(result) , 
            "message"  : "Successful"
            
            }
    total_pages = (result.count() / page_size)

    if result.count() % int(page_size) == 0 :
        
        print(total_pages, "total pages if block ")
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : total_pages ,
            "message" : "Successful"
            
            }

    else :
        data = []
        for i in result:
            data.append(i)
        return  {
            
            'Items' : data[start : end] , 
            "Page" :  page_num , 
            "PerPage" : page_size , 
            "Totaldata" : result.count(),
            "TotalPages" : int(total_pages + 1),
            "message"  : "Successful"
            
            }
        
        
        
@app.get('/Business_accepted_payment_methods/{id}/' , status_code=status.HTTP_200_OK)
def by_id(  id : int ,user : _schema.User = _fastapi.Depends(_services.get_current_user), db : Session = Depends(get_db)):

    
    new_blog = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id).first()
    if not new_blog :
        # raise HTTPException (status_code= status.HTTP_404_NOT_FOUND , detail= f'blog with this id {id} not found ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f'Data with this id : {id} not found'},)
    
    #validation for check the id delete or not.
    check = validation.Business_accepted_payment_methods_deletecheck (id , db)
    if check == "data_already_delete" :
        # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f" Id : {id} is already Deleted"},)
    
    
    new_blog1 = []
    
    new_blog1.append(new_blog)
    return {
        
        
            "Item" : new_blog1,
            "message" : "Successful"
            
            }



#This api is for forgate_password
'''
When user link is expired after sending mail(afetr 3 minutes),
resend mail again so we need email of the user 

from front-end he give UUID only.
i will fetch the email from OTP table and give email as a response. 

* Name of APi - Get_by_ucode
'''


@app.get('/get_by_ucode/' , status_code=status.HTTP_200_OK)
def fetch_email( UUID : str , db : Session = Depends(get_db)):
    

    result = db.query(models.Otp_table).filter(models.Otp_table.uuid  ==  UUID).first()
    if not result:
        return JSONResponse(status_code=status.HTTP_200_OK,content={"message":"UUID not found "},)
    return {
        
        'email' : result.email , 
        "message" : 'Successful'
    }
    



@app.post('/get_by_token/' , status_code=status.HTTP_200_OK)
def fetch_email( request : schema._token_from ,db : Session = Depends(get_db)):
   

    result = db.query(models.Token_store).filter(models.Token_store.token  ==  request.token).first()
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"User not found"},)
    

    result1 = db.query(models.User).filter(models.User.email == result.user_email)
    if not result1 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":"Email not found"},)
    

    data1 = {}
    data1['email'] = result.user_email
    data1['f_name'] = result1.first().f_name
    data1['l_name'] = result1.first().l_name

    list_data = []
    list_data.append(data1)
        
    return {
        

        'Item' : list_data , 
        "message" : 'Successful'
    }
    
