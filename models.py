from ast import Str
from decimal import Clamped
from unicodedata import category

from tomlkit import integer
import database 
from sqlalchemy import BigInteger,  Column, Float, Integer, String , ForeignKey , DateTime , Boolean , Date  , Time
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy_utils import URLType
from sqlalchemy_utils import EmailType
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import JSON



class Business_categorys(database.Base):
    __tablename__ = 'business_category'
    id = Column(Integer , primary_key = True)
    name = Column(String,  nullable=False , unique= False)
    status = Column(Boolean,  nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow,  nullable=False)

class Business_sub_categorys(database.Base):
    __tablename__ = 'business_sub_category'
    id = Column(Integer , primary_key = True)
    name = Column(String, nullable=False , unique= False)
    status = Column(Boolean ,  nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow,  nullable=False)
    business_category_id = Column(Integer, ForeignKey("business_category.id")) 
    Business_category = relationship("Business_categorys")

    
class Countries(database.Base):
    __tablename__ = 'countries'
    id = Column(Integer ,primary_key = True)
    name = Column(String ,  nullable=False)
    flag_image = Column(URLType ,  nullable=False)
    status = Column(Boolean ,  nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class States(database.Base):
    __tablename__ = 'states'
    id = Column(Integer ,primary_key = True)
    name = Column(String ,  nullable=False)
    status = Column(Boolean , nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    countries_id = Column(Integer, ForeignKey("countries.id"))
    Countries = relationship("Countries")

class Cities(database.Base):
    __tablename__ = 'cities'
    id = Column(Integer ,primary_key = True)
    name = Column(String ,  nullable=False)
    status = Column(Boolean , nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"))
    States = relationship("States")

class Businesses(database.Base):
    __tablename__ = 'business'
    id = Column(Integer, primary_key = True)
    name = Column(String ,  nullable=False)
    parent_id = Column(Integer , nullable=True , default=None) # it will store the id of parent_business from the business table it self 

    logo_large = Column(URLType ,  nullable=True)
    logo_small = Column(URLType ,  nullable=True)
    information = Column(String,  nullable=True ,  default=None)
    rating = Column(Integer) # overall average of rating of business . 
    established_year = Column(Date,  nullable=False)
    status = Column(Boolean , nullable = False )
    address = Column(String, default=None)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    category_id = Column(Integer, ForeignKey("business_category.id"), nullable=False)
    sub_category_id = Column(Integer,  ForeignKey("business_sub_category.id"))
    country_id = Column(Integer, ForeignKey("countries.id"),  nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"),  nullable=False)  
    city_id = Column(Integer, ForeignKey("cities.id"),  nullable=False)  
    
    Category = relationship("Business_categorys")
    Sub_category = relationship("Business_sub_categorys")
    Country = relationship("Countries")
    States = relationship("States")
    City = relationship("Cities")
    
    
    
    

class Business_faqs(database.Base):
    __tablename__ = 'business_faqs'
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"))
    question = Column(String  , nullable = True )
    answar = Column(String)
    status = Column(Boolean , nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    

class Business_products(database.Base):
    __tablename__ = 'business_product'
    id = Column(BigInteger , primary_key= True)
    business_id = Column(Integer, ForeignKey("business.id") ,nullable = False)
    name = Column(String  , nullable = False)
    descriptions = Column(String , nullable = False)
    image =Column(URLType ,  nullable=False)
    price = Column(Float , nullable = False)
    status = Column(Boolean , nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    

class Amenities_services(database.Base):
    __tablename__ = 'amenities_services'
    id = Column(Integer , primary_key = True )
    name = Column(String , nullable = False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class  Business_amenities_services(database.Base):
    __tablename__ = "business_amenities_services"
    id = Column(Integer, primary_key = True,nullable= False)
    business_id = Column(Integer , ForeignKey("business.id"))
    amenity_service_id = Column(Integer,  ForeignKey("amenities_services.id"))
    phone_number = Column(BigInteger ,nullable= False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    Businesses = relationship("Businesses")
    Amenities_services =  relationship("Amenities_services")
    
    

class Payment_methods(database.Base):
    __tablename__ = "payment_method"
    id = Column(Integer , primary_key = True )
    name = Column(String, nullable = False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    
    
class Reaction_types(database.Base):
    __tablename__ = "reaction_types"
    id = Column(Integer , primary_key = True)
    type = Column(String)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    
     
class Business_accepted_payment_methods(database.Base):
    __tablename__ = "business_accepted_payment_methods"
    id = Column(Integer , primary_key = True)
    business_id =  Column(Integer, ForeignKey("business.id") , nullable = False)
    payment_method_id = Column(JSONB(Integer,  ForeignKey("payment_method.id")))
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class User_group_types(database.Base):
    __tablename__ = "user_group_type"
    id = Column(Integer , primary_key = True)
    group_name = Column(String , nullable = False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)

import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm 
import passlib.hash as _hash 
import database as _database 






class User(_database.Base):
    __tablename__ = "user"
    id = _sql.Column(_sql.Integer , primary_key= True , index= True )
    f_name = _sql.Column(_sql.String  )
    l_name = _sql.Column(_sql.String  )
    User_group_types_id = _sql.Column(Integer, ForeignKey("user_group_type.id") , nullable = False)
    email = _sql.Column(_sql.String , unique= True , index= True )
    hashed_password = (_sql.Column(_sql.String))
    status = Column(Boolean , nullable = False)
    created_at = _sql.Column(_sql.DateTime , default=_dt.datetime.utcnow)
    updated_at = _sql.Column(_sql.DateTime , default=_dt.datetime.utcnow)
    token_exp_time = _sql.Column(_sql.DateTime , default=_dt.datetime.utcnow)

    def varify_password(self , password : str):
        return _hash.bcrypt.verify(password , self.hashed_password)
    
    


class User_detail(database.Base):
    __tablename__ = "userdetail"
    id = Column(Integer , primary_key = True)
    user_id = Column(Integer, ForeignKey("user.id") , nullable = False)
    image = Column(URLType)
    city_id = Column(Integer, ForeignKey("cities.id") , nullable = False)
    state_id = Column(Integer, ForeignKey("cities.id") , nullable = False)
    country_id = Column(Integer, ForeignKey("countries.id") , nullable = False)
    pincode = Column(Integer , nullable = False)
    date_of_birth =  Column(DateTime)
    gender = Column(String , nullable = False)
    mobile = Column(BigInteger , nullable = False)
    status =  Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class Business_reaction(database.Base):
    __tablename__ = "business_reaction"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False) 
    reaction_types_id = Column(JSONB(Integer,  ForeignKey("reaction_types.id")))
    user_id = Column(Integer, ForeignKey("user.id"),nullable = False) 
    status =  Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    

class Business_ratings(database.Base):
    __tablename__ = "business_ratings"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False) 
    user_id =  Column(Integer, ForeignKey("user.id"),nullable = False)
    rating = Column(Float , nullable = True)
    status =  Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)





class Business_reviews(database.Base):
    __tablename__ = "business_reviews"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False) 
    user_id =  Column(Integer, ForeignKey("user.id"),nullable = False)
    review = Column(String , nullable = True)
    status =  Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
  
    

    
    
class Website_link(database.Base):
    __tablename__ = "website_link"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False)
    link = Column(String , nullable = False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)

class Social_media(database.Base):
    __tablename__ = "social_media"
    id = Column(Integer , primary_key = True )
    name = Column(String , nullable = False )
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class Business_social_website_links(database.Base):
    __tablename__ = "business_social_website"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False)
    social_media_id = Column(Integer, ForeignKey("social_media.id"),nullable = False)
    link = Column(String , nullable=False)
    status = Column(Boolean , nullable = False) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class Business_images(database.Base):
    __tablename__ = "business_images"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False)
    image = Column(URLType , nullable = False)
    status = Column(Boolean , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)

class Business_working_hours(database.Base):
    __tablename__ = "business_working_hours"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"),nullable = False)
    day_of_week = Column(String , nullable = False)
    open_time =  Column(Float , nullable = False)
    close_time =  Column(Float , nullable = False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)

class Tags(database.Base):
    __tablename__ = "tags"
    id = Column(Integer , primary_key = True)
    name = Column(String)
    status = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)


class Business_tags(database.Base):
    __tablename__ = "business_tags"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))
    status = Column(Boolean)
    phone_number = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)

class Business_Professionals(database.Base):
    __tablename__ = "business_professional"
    id = Column(Integer , primary_key = True)
    name = Column(String ,unique=True, )
    business_id = Column(Integer, ForeignKey("business.id"))
    designtion  = Column(String , nullable = False)
    speciality  = Column(String )
    qualification = Column(String , nullable = False)
    email = Column(EmailType)
    phone_number = Column(BigInteger)
    address = Column(String)
    status = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    


class  Business_phone_numbers(database.Base):
    __tablename__ = "business_phone_numbers"
    id = Column(Integer , primary_key = True)
    business_id = Column(Integer, ForeignKey("business.id"))
    phone_type = Column(String)
    number = Column(BigInteger)
    description = Column(String)
    is_primary =  Column(Boolean)
    status = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    updated_at =  Column(DateTime, default=datetime.datetime.utcnow ,  nullable=False)
    
    

class Otp_table(_database.Base):
    __tablename__ = "otptable"
    id =  _sql.Column(_sql.Integer , primary_key= True , index= True )
    email = _sql.Column(_sql.String)
    current_time = Column(DateTime, default=datetime.datetime.now )
    uuid = _sql.Column(_sql.String)



class Token_store(_database.Base):
    __tablename__ = "token_table"
    id =  _sql.Column(_sql.Integer , primary_key= True , index= True )
    
    token =  _sql.Column(_sql.String )
    user_email = _sql.Column(_sql.String)

