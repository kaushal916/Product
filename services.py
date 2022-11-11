from operator import contains
import database as _database 
import models as _models
import sqlalchemy.orm as _orm 
import schema as _schema
import email_validator as  _email_check 
import passlib.hash as _hash
import fastapi as  _fastapi
import jwt as _jwt 
import fastapi.security as _security 
import re
import models
import yaml
from datetime import datetime, timedelta
import datetime
import validation
import database
from sqlalchemy.orm import sessionmaker



with open("config.yaml", "r") as yamlfile:
    config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)


_JWT_SECRET = "thisisnotverysafe"


oauth2schema = _security.OAuth2PasswordBearer("/api/token")
def _create_database():
    return _database.Base.metadata.create_all(bind = _database.engine)


def get_db ():
    db = _database.SessionLocal()
    try :
        yield db 
    finally :
        db.close()


async def get_user_by_email(email : str  , db : _orm.Session ):
    return db.query(_models.User).filter(_models.User.email == email).first()


# async def create_user(user : _schema.UserCreate , db : _orm.Session):
#     try :
#         valid = _email_check.validate_email(email = user.email)
#         email = valid.email
#         if len(user.password) < 5 :
#             raise _fastapi.HTTPException(status_code=404 , detail= "password should be gretter than 5 charcter and number  ")

#     except _email_check.EmailNotValidError:
#         raise _fastapi.HTTPException(status_code=404 , detail= "please enter a valid email ")
    
    
#     hashed_password = _hash.bcrypt.hash(user.password)
#     user_obj = _models.User(f_name = user.f_name , l_name = user.l_name, User_group_types_id = user.user_group,email = email  , hashed_password = hashed_password)
    
    
#     db.add(user_obj)
#     db.commit()
#     db.refresh(user_obj)
#     return user_obj



# async def create_torken (user : _models.User):
#     user_schema_obj = _schema.User.from_orm(user)
    
#     user_dict = user_schema_obj.dict()
#     del user_dict["created_at"]
    
    
#     token = _jwt.encode(user_dict,_JWT_SECRET )
    
    
#     return dict(access_token = token , token_type = "bearer")


async def create_user(user : _schema.UserCreate , db : _orm.Session):
    # try :
    #     valid = _email_check.validate_email(email = user.email)
    #     email = valid.email
    #     # if len(user.password) < 5 :
    #     #     raise _fastapi.HTTPException(status_code=404 , detail= "password should be gretter than 5 charcter and number  ")

    # except _email_check.EmailNotValidError:
    #     return "1"

    if user.l_name == "":
        user.l_name = None
    check_email = db.query(models.User).filter(models.User.email == user.email ).first()
    if check_email :
        return "1"
        # raise _fastapi.HTTPException(status_code=404 , message= "please enter a valid email")
    
    # This validation is for f_name can not be null 
    if user.f_name == "":
        return "f_name_null"
    if len(user.f_name)  <  2 :
        return "length_of_fname"



# DATABASE_URI = "postgresql://" + data['database']['username'] + ":" + data['database']['password'] + "@localhost/"+ data['database']['db']

    if user.password == "":
        return "password_null"
    
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,50}$"
    pat = re.compile(reg)         
    mat = re.search(pat, user.password)
    
    if mat:
        print("Password is valid.")
    else:
        return "password_error"
        # raise _fastapi.HTTPException(status_code=404 , detail= "Should have at least one number\nShould have at least one uppercase and one lowercase character\nShould have at least one special symbol\nShould be between 1 to 100 characters long.")

    if user.user_group == 0 :
        return "user_group_zero"

    data = db.query(models.User_group_types).filter(models.User_group_types.id == user.user_group ).first()
    if data and data.status == True:
        pass
    else :
        return "user_group_not_exist"


    
    hashed_password = _hash.bcrypt.hash(user.password)
    user_obj = _models.User(f_name = user.f_name , l_name = user.l_name, User_group_types_id = user.user_group,email = user.email  , hashed_password = hashed_password , status = True)
    
    
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj



async def create_torken (user : _models.User):
    user_schema_obj = _schema.User.from_orm(user)
    
    user_dict = user_schema_obj.dict()
    del user_dict["created_at"]
    
    
    token = _jwt.encode(user_dict,_JWT_SECRET )
    print("********************************8")
    print(user_dict)
    
    
    

    new_token = []
    new_token.append(token)
    data = models.Token_store(token=token, user_email=user.email)
    
    Session = sessionmaker(bind = database.engine)
    session = Session()
    
    token_check = session.query(models.Token_store).filter(models.Token_store.token == token)
    if not token_check.first():
    
        session.add(data)
        session.commit()
        
    return {
        
            'item': new_token  ,
             "message" : "successful"
             
            }


async def authenticate_user(email : str , password : str , db : _orm.Session):
    user = await get_user_by_email(email = email , db = db )
    if not user :
        return False
    if not user.varify_password(password = password ):
        return False 
    return user 


async def get_current_user(db : _orm.Session = _fastapi.Depends(get_db) , token : str = _fastapi.Depends(oauth2schema)):
    
    try :
        payload = _jwt.decode(token , _JWT_SECRET , algorithms= ["HS256"])
        user = db.query(_models.User).get(payload["id"])

        # Token Expire
        print(user.email, "User email")
        token_exp_time = db.query(models.User).filter(models.User.email == user.email).first()
        time = token_exp_time.token_exp_time
        print(time ,"token_exp_time read from db ")
        now =  datetime.datetime.now()
        print(now , "current_time")
        
        
        if time <  now :
            print('time expire')
            validation.new()

        else:
            print('notworking')
    except:
        raise _fastapi.HTTPException(
            status_code= 401 ,
            detail= "Token expire"
        )
        
    return _schema.User.from_orm(user)

    

'''




@app.get("/items/", response_class=HTMLResponse)
async def read_item(request: Request):
    

    return templates.TemplateResponse("forgate.html", {"request": request})


otpnumber=""
for i in range(4):
    otpnumber+=str(r.randint(1,9))


# if email id valid then send the mail to user account 
@app.post('/submitform')
async def handel_form(request: Request , email : str = Form(...),db : Session = Depends(get_db)):

    data = db.query(models.User).filter(models.User.email == email).first()
    if data:
        
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "hanishkaushal00@gmail.com"
        receiver_email = email
        password = "ndqgzekzsgbkjqnd"
        message = f"""\
        Varification 

        Varification code :{otpnumber} """

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


        return templates.TemplateResponse("validate.html" , {"request": request})
    
    else:
        return 'mail not found  '


# check the otp is matched or not 
@app.post('/otpvalidation')
async def validation_otp(otp : str = Form(...)):
    if otp == otpnumber :
        print('otp match successfully ')
        return "otp match successfully "
    else:
        print("otp did not match ")
        return "otp didn't match"
        


'''