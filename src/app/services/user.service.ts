import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http:HttpClient) { }
  // List Of category table 
  listcategory(){
    let data=  this.http.get(environment.baseURL + 'category/');
    return data
  }
  // Log in user according to user table  
  userlogin(data:any){
    return this.http.post(environment.baseURL + 'api/token/',data)
  }
 
  // Create User
  createuser(data:any){
    return this.http.post(environment.baseURL+ 'api/users',data)
  }
  //Group of user like "admin"
  usergroup(){
    return this.http.get(environment.baseURL + 'user_group')
  }
  
  //Get login token from the local storage 
  gettoken(){  
    return !!localStorage.getItem("token");  
  }
} 
