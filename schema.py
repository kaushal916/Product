
from datetime import datetime 

from pydantic import BaseModel , Field , SecretStr 
from sqlmodel import ARRAY, JSON, Field, SQLModel

from typing import Union
from fastapi import Body  , UploadFile , File
from typing import Optional
class Bloga(BaseModel):
    title : str
    body : str 
    name : str 
    image : str
    status : str
    created_at : str
    updated_at :  str

class user_login(BaseModel):
    username : str
    password : str


class category (BaseModel):
    name : str 
    
    
class sub_category(BaseModel):
        
    name : str
    business_category_id : int


class countries(BaseModel):
    name : str 


class state (BaseModel):
    name : Union[str, None] 
    countries_id  : Union[int, None] 
    


class city(BaseModel):
    name : str
    state_id  : int 

# class businesses(BaseModel):
#     name : str
#     category_id : int
#     parent_id : int
#     sub_category_id : int
#     country_id : int
#     state_id : int
#     city_id : int
#     information : str 
#     rating : float
#     established_year : datetime
#     address : str
    


class business_faqs(BaseModel):
    business_id : int = Field(...)
    question : str 
    answar : str
    schema_extra = {
        "example": {
            "fullname": "Mark Watney",
            "email": "mark.watney@nasa.gov",
            "course_of_study": "Botanics",
            "year": 4,
            "gpa": "4.0",
        }
    }
    
    
class Amenities_services(BaseModel):
    name : str 


class Business_amenities_services(BaseModel):
    business_id : int
    amenity_service_id : int
    phone_number : int

class Payment_methods(BaseModel):
    name : str 


class User_group(BaseModel):
    group_name : str 
    
    
    
# this is for authentication for user 
import datetime as _dt 
import pydantic as _pydantic

class _Userbase(BaseModel):
    email : str 
    
class UserCreate(_Userbase):
    
    f_name : str 
    l_name : Union[str, None] = None
    password : str 
    # conf_password : str 
    user_group :Optional[int] = None
    class Config:
        orm_mode = True

class UserCreateschema(_Userbase):
    f_name : str 
    l_name : str 
    user_group : int
    class Config:
        orm_mode = True
        
class UserCreateschema1(BaseModel):
    f_name : str 
    l_name : str 

class User (_Userbase):
    id : int 
    created_at : _dt.datetime
    
    class Config :
        orm_mode = True 
        
class passchange(BaseModel):
    uuid : str  
    new_password : str


class Business_reaction(BaseModel):
    business_id : int
    reaction_types_id : int
    user_id: int


class emailschema(BaseModel):
    email : str
    
class business_rating (BaseModel):
    business_id : int
    user_id : int
    rating :Optional[float] = None
    
class Business_reviews(BaseModel):
    business_id :int
    user_id : int
    review :Optional[str] = None


class Business_reviews1(BaseModel):

    review :Optional[str] = None
    
class Website_link(BaseModel):
    business_id : int
    link : str 

class social_media(BaseModel):
    name: str 

class Business_social_website_links(BaseModel):
    business_id : int 
    social_media_id : int
    link : str
class Business_social_website_links1(BaseModel):
    link : str
    
    
class Business_working_hours(BaseModel):
    business_id : int
    day_of_week : int
    open_time : Optional[float] = None
    close_time : Optional[float] = None

class Business_working_hours1 (BaseModel):
    day_of_week :Optional[int] = None
    open_time : Optional[float] = None
    close_time : Optional[float] = None
    
    
    
class Tags(BaseModel):
    name : str

class Business_tags(BaseModel):
    business_id : int
    tag_id : int 
    phone_number :Optional[int] = None 
    
    
class Business_Professionals(BaseModel):
    name : str 
    business_id : int
    designtion  : str
    speciality : str 
    qualification : str 
    email : str 
    phone_number : int 
    address : str 
    
    
class Business_phone_numbers(BaseModel):
    business_id : int 
    phone_type : str
    number : int 
    description : str 
    is_primary : Optional[bool] = None
    

class Reaction_types(BaseModel):
    type : str 



class Business_method_payment_id(BaseModel):
    business_id :int
    payment_method_id :int 


class _token_from(BaseModel):
    token : str 
    