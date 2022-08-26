import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';
import { Location } from '@angular/common';
import { AlertService } from '../../alert/alert.service';

@Component({
  selector: 'ngx-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  formdata = new FormData()
  title: string
  constructor(private userService:UserService,
    private router: Router,
    private _location: Location,
    private alertService: AlertService ) {
    
  }
  
  ngOnInit(): void {
    this.checkToken()
  }


  loginFormGroup= new FormGroup({
    username: new FormControl('',[Validators.required,Validators.email]), 
    password: new FormControl('',[Validators.required,Validators.minLength(5)]), 
  });

  loginUserForm(data:any){
    this.formdata.append("username",data.username)
    this.formdata.append("password",data.password)
    this.userService.userlogin(this.formdata).subscribe((result: any)=>{
      console.log('Token',result);
      localStorage.setItem('token', result.access_token);
      this.router.navigate(['/pages/dashboard']);
      this.alertService.successalert('Logg in Success','success')
    },
    error =>{
      this.title = error.error.message
      console.log(this.title);
      
      this.alertService.successalert(this.title,'warning')
      
    });
  }

  get email_validate(){
    return this.loginFormGroup.get('username') 
  }

  get password_validate(){
    return this.loginFormGroup.get('password') 
  }

  get login_detail_valodator(){
    return this.loginFormGroup.get('logindetail') 
  }

  checkToken(){
    if(!localStorage.getItem("token")){ 
      this.router.navigate(['/login']);
    }
    else{
      this._location.back();
    }
  }
  

}
