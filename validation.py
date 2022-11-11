import fastapi as _fastapi
import re
import email_validator as  _email_check 
import database
from fastapi import  Depends , status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
# this validation is for schema 


def get_db():
    db = database.SessionLocal()
    try :
        yield db 
    finally:
        db.close()



def digit_validation(request):
    a = str(request).isdigit()
    if a == False :
        return False 

def name_validation(request):
    
    if request== "":
        return True

def length_validation(request):
    if len(request)  < 2 :
        return True
        
def int_check(request):
    if request.isdigit():
        return True
def id_check(request):
    if request == 0 :
        return True
def check_business_category_id(name, db : Session = Depends(get_db)):
    data = db.query(models.Business_categorys).filter(models.Business_categorys.name == name).first()
    if data.status == True :
        return True 
    
    
#category 
def delete_datacheck (id ,  db : Session = Depends(get_db) ):
    data = db.query(models.Business_categorys).filter(models.Business_categorys.id == id).first()
    if data.status == False :
        return True

def deletecheck(id ,   db : Session = Depends(get_db)):

    data = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).first()
    if data.status == False:
        return True






#Login 
def email_validation(email ,  db : Session ):
    # try:

        data = db.query(models.User).filter(models.User.email == email)
        print(data)
        if data.first():
            print('user email found in db')
        else:
            return True 

# this validation is for Login time expire
def new():
    raise _fastapi.HTTPException(status_code=404 , detail= "Password cannot be blank")
    



def user_exist_status_check(userid , db : Session = Depends(get_db)):
    check_id_exist = db.query(models.User).filter(models.User.id == userid).first()
    
    if not check_id_exist:
        return "user_id_not_exist"
    if check_id_exist.status == False :
        return "user_id_status_false"
    

def city_exist_status_check (cityid , db : Session = Depends(get_db) ) :
    check_city_id =  db.query(models.Cities).filter(models.Cities.id == cityid).first()

    if not check_city_id :
        return "city_id_not_exist"

    if check_city_id.status == False:
        return "city_id_status_false"




def state_exist_status_check (stateid ,  db : Session = Depends(get_db)):
    check_city_id =  db.query(models.States).filter(models.States.id == stateid).first()
    if not check_city_id :
        return "state_id_not_exist" 
    if check_city_id.status == False :
        return "state_id_status_false" 
        
    


def country_exist_status_check (countryid , db : Session = Depends(get_db)):
    check_country_id =  db.query(models.Countries).filter(models.Countries.id == countryid).first()
    
    if not check_country_id :
        return "country_id_not_exist"
    if check_country_id.status == False :
        return "country_id_status_false"
    
    
    
        

def business_exist_status_check( business_id , db : Session = Depends(get_db)):
    check_country_id =  db.query(models.Businesses).filter(models.Businesses.id == business_id).first()

    if not check_country_id :
        return "business_id_not_exist"
    if check_country_id.status == False :
        return "business_id_status_false"


def payment_exist_status_check( payment_id , db : Session = Depends(get_db)):
    check_country_id =  db.query(models.Payment_methods).filter(models.Payment_methods.id == payment_id).first()

    if not check_country_id :
        return "payment_id_not_exist"
    if check_country_id.status == False :
        return "payment_id_status_false"
    
    
def reaction_exist_status_check( reaction_id , db : Session = Depends(get_db)):
    check_reaction_id =  db.query(models.Reaction_types).filter(models.Reaction_types.id == reaction_id).first()

    if not check_reaction_id :
        return "reaction_id_not_exist"
    if check_reaction_id.status == False :
        return "reaction_id_status_false"
    
    
def business_rating_deletecheck (id , db : Session = Depends(get_db) ):
    
    s = db.query(models.Business_ratings).filter(models.Business_ratings.id == id)
    if s.first().status == False :
        return "data_already_delete"

def Business_accepted_payment_methods_deletecheck (id , db : Session = Depends(get_db) ):
    
    s = db.query(models.Business_accepted_payment_methods).filter(models.Business_accepted_payment_methods.id == id)
    if s.first().status == False :
        return "data_already_delete"


def business_review_deletecheck(id ,db : Session = Depends(get_db) ):
    

    s = db.query(models.Business_reviews).filter(models.Business_reviews.id == id)
    if s.first().status == False :
        return "data_already_delete"


def websitelink_deletecheck (id , db : Session = Depends(get_db)):

    s = db.query(models.Website_link).filter(models.Website_link.id == id)
    if s.first().status == False :
        return "data_already_delete"




def Social_media_deletecheck(id , db : Session = Depends(get_db)):
    s = db.query(models.Social_media).filter(models.Social_media.id == id)
    if s.first().status == False :
        return "data_already_delete"

def Tags_deletecheck(id , db : Session = Depends(get_db)):
    s = db.query(models.Tags).filter(models.Tags.id == id)
    if s.first().status == False :
        return "data_already_delete"

def Reaction_type_deletecheck(id , db : Session = Depends(get_db)):
    s = db.query(models.Reaction_types).filter(models.Reaction_types.id == id)
    if s.first().status == False :
        return "data_already_delete"


def Business_social_website_links_deletecheck(id , db : Session = Depends(get_db)):
    
    s = db.query(models.Business_social_website_links).filter(models.Business_social_website_links.id == id)
    if s.first().status == False :
        return "data_already_delete"


def Businessimage_deletecheck(id , db : Session = Depends(get_db)):
    
    s = db.query(models.Business_images).filter(models.Business_images.id == id)
    if s.first().status == False :
        return "data_already_delete"




def Business_image_deletecheck(id , db : Session = Depends(get_db)):
    
    s = db.query(models.Business_images).filter(models.Business_images.id == id)
    if s.first().status == False :
        return "data_already_delete"




def social_exist_status_check (id , db : Session = Depends(get_db) ):
    s = db.query(models.Social_media).filter(models.Social_media.id == id)
    
    if not s.first():
        return "data_not_exist"
    if s.first().status == False :
        return "data_already_delete"





def tag_id_status_check (id ,db : Session = Depends(get_db)  ):
    
    data = db.query(models.Tags).filter(models.Tags.id == id ).first()
    if not data : 
        return "Tags_id_not_found"
    if data.status == False :
        return "tags_status_false"





# signup 
#password_validation

# def password_validation(password ):
#     if password == "":
#         return "password_null"
#         # raise _fastapi.HTTPException(status_code=404 , detail= "Password cannot be blank")

        
#     # if password != conf_password :
#     #     raise _fastapi.HTTPException(status_code=404 , detail= "Password not match")
    
#     if len(password) < 6 :
#         raise _fastapi.HTTPException(status_code=404 , detail= "Length should be 6 ")
        
#     reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{1,1000}$"
#     pat = re.compile(reg)         
#     mat = re.search(pat, password)
#     if mat:
#         print("Password is valid.")
#     else:
#         raise _fastapi.HTTPException(status_code=404 , detail= "Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long.")

































def id_validation(request):
    
    if request == 0 :
        # raise _fastapi.HTTPException(status_code=404 , detail= 'We can not proceed with 0')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'We can not proceed with 0'},)
    
def business_category_id(request):
    if request.business_category_id == 0 :
        # raise _fastapi.HTTPException(status_code=404 , detail= 'Enter sub_category id ')
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":'Enter sub_category id'},)
    
    
    
    


# This validation is for request body 


def name_validation1(request):
    if request == "":
        return True
        # raise _fastapi.HTTPException(status_code=404 , detail= " Name field is required")

    if len(request)  < 2 :
        raise _fastapi.HTTPException(status_code=404 , detail= " Name field Length should be greterthan 2 character")
# def digit_validation(request):
#     if request.isdigit():
#         raise _fastapi.HTTPException(status_code=404 , detail= "category name should be greterthan 2 character")

# def password_validation1(password):
    
#     if password == "":
#         raise _fastapi.HTTPException(status_code=404 , detail= "Password cannot be blank")

#     if len(password) < 6 :
#         raise _fastapi.HTTPException(status_code=404 , detail= "Length should be 6 ")
        
#     reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{1,1000}$"
#     pat = re.compile(reg)         
#     mat = re.search(pat, password)
#     if mat:
#         print("Password is valid.")
#     else:
#         raise _fastapi.HTTPException(status_code=404 , detail= "Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long.")









# def category(category_id , db : Session = Depends(get_db) ):
#     try:
#         data = db.query(models.Business_categorys).filter(models.Business_categorys.id == category_id)
#         if data.first():
#             print('Business_categorys id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"Category id {category_id} is not found in Business_Category table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"Category id {category_id} is not found in Business_Category table ")
        
        
# def sub_category(sub_category_id , db : Session = Depends(get_db)):
#     try:
#         data = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == sub_category_id)
#         if data.first():
#             print('sub_category id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"Sub_category id {sub_category_id} is not found in Sub_category table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"Sub_category id {sub_category_id} is not found in Sub_category table ")
        
# def country(country_id , db : Session = Depends(get_db)):
#     try:
#         data = db.query(models.Countries).filter(models.Countries.id == country_id)
#         print(data)
#         if data.first():
#             print('country id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"Country id {country_id} is not found in Country table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"Country id {country_id} is not found in Country table ")
        

# def state(state_id , db : Session = Depends(get_db)):
#     try:
#         data = db.query(models.States).filter(models.States.id == state_id)
#         print(data)
#         if data.first():
#             print('state id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"State id {state_id} is not found in State table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"State id {state_id} is not found in State table ")
        

# def city(city_id , db : Session = Depends(get_db)):
#     try:
#         data = db.query(models.Cities).filter(models.Cities.id == city_id)
#         print(data)
#         if data.first():
#             print('Cities id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"City id {city_id} is not found in Cities table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"City id {city_id} is not found in Cities table ")


# def parent_id_validation(parent_id , db : Session = Depends(get_db)):
#     try:
#         data = db.query(models.Businesses).filter(models.Businesses.id == parent_id)
#         print(data)
#         if data.first():
#             print('parent_id id found ')
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"parent_id  {parent_id} is not found in Business table ")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"parent_id  {parent_id} is not found in Business table ")
        




# def established_year_validation (established_year):
#     if established_year :
#         pass
    
#     else:
#         raise _fastapi.HTTPException(status_code=404 , detail= "Established_year field is required")
# def address_validation(address):
#     if len(address) < 5 :
#         raise _fastapi.HTTPException(status_code=404 , detail= "Address should be greaterthan 10 Character")


# def information_validation(information):
#     if len(information) < 10 :
#         raise _fastapi.HTTPException(status_code=404 , detail= "Information should be greaterthan 5 Character")





# # This function is responsible for check business id is exist or not 
# def Business_faqs_validation(business_id , db : Session = Depends(get_db)):
#     try :
#         data = db.query(models.Businesses).filter(models.Businesses.id == business_id)
#         if data.first():
#             pass
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"Business id :  {business_id} is not exist in our Business table")
#     except:
        
#         raise _fastapi.HTTPException(status_code=404 , detail= f"Business id :  {business_id} is not exist in our Business table")
        
            
# def amenity_service_validation(amenity_service_id , db : Session = Depends(get_db)):
#     try :
#         data = db.query(models.Amenities_services).filter(models.Amenities_services.id == amenity_service_id)
#         if data.first():
#             pass
#         else:
#             raise _fastapi.HTTPException(status_code=404 , detail= f"Amenities_services id :  {amenity_service_id} is not exist in our Amenities_services table")
#     except:
#         raise _fastapi.HTTPException(status_code=404 , detail= f"Amenities_services id :  {amenity_service_id} is not exist in our Amenities_services table")



# def Phonenumber_validation(phonenumber):
#     if len(phonenumber) == 10  and phonenumber.isdigit() == True :
#         pass
#     else:
#         raise _fastapi.HTTPException(status_code=404 , detail= "Phone number should be 10 digit integer ")
        
    
# # validation for status = False 






# '''
# This validation is for 
# 1)If user send request to update something and the request data (status == False)
# 2) If user send to request to update name and the name is already exist 
# '''

# def category_update_status(id, name,db : Session = Depends(get_db)):
#     print("!@$#$!@@@$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

#     data = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).first()
#     if data.status == False:
#         print("ok55555555555555555555prakash5555555555555555555555555555555555")
#         raise _fastapi.HTTPException(status_code=404 , detail= f"This id is Already deleted")
#         # return JSONResponse(content='json_compatible_item_data')

#     data1 = db.query(models.Business_categorys).filter(models.Business_categorys.name == name).first()
#     print('ok')
#     if data1:
#         print("okkkkkkkkkkkkkkkkkkkkkkkkk")
#         # raise _fastapi.HTTPException(status_code=404 , detail= f"{name} already exist")
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"{name} already exist"},)
#         # return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"{name} already exist"},)
    

    
# # this validation is used for check the user requested data is deleted or not. 

# def category_update_status1(id ,db : Session = Depends(get_db) ):
#     data = db.query(models.Business_categorys).filter(models.Business_categorys.id == id ).first()
#     if data.status == False:
#         # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f" Id : {id} is already Deleted"},)





# def subcategory_status(id , name , db : Session = Depends(get_db)):
#     print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5")
#     print(id)
#     print(name)

        
#     data = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id).first()
#     print(data.name)
#     if data.status == False :
#         # raise _fastapi.HTTPException(status_code=404 , detail= f" Id : {id} is already Deleted")
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f" Id : {id} is already Deleted"},)
    

        
        
#     data1 = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.name == name ).first()
#     if data1:
#         # raise _fastapi.HTTPException(status_code=404 , detail= f"{name} already exist")
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":f"{name} already exist"},)
    


# def sub_category_delete_check(id , db : Session = Depends(get_db)) :
#     data = db.query(models.Business_sub_categorys).filter(models.Business_sub_categorys.id == id ).first()
#     if data.status == False:
#         print("***************************************")
#         return {"msg" : "ok"}
#         # raise _fastapi.HTTPException(status_code=404 , detail= f"{id} already Deleted") 
#         # return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message": f"{id} already Deleted"})
        
    
