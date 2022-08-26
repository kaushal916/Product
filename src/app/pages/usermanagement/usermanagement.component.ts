import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormGroup,Validators } from '@angular/forms';
import { FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'ngx-usermanagement',
  templateUrl: './usermanagement.component.html',
  styleUrls: ['./usermanagement.component.scss']
})
export class UsermanagementComponent implements OnInit {
  usergroup :any=[]
  constructor(private userService:UserService,
    private router : Router) {
    this.userService.usergroup().subscribe(group=>{
      this.usergroup = group
      console.log(group)
    })
  }
  registerFormGroup= new FormGroup({
    email: new FormControl('',[Validators.required,Validators.email]), 
    f_name: new FormControl('',[Validators.required,Validators.minLength(3)]),
    l_name: new FormControl(''),
    user_group: new FormControl('',[Validators.required]),
    password: new FormControl('',[Validators.required,Validators.minLength(5)]), 
    cpassword: new FormControl('',[Validators.required,Validators.minLength(5)]), 
  })

  ngOnInit(): void {
  }

  registrationUserSubmit(data : any){
    console.log(this.registerFormGroup.value)
    // this.userService.userbyemail(data).subscribe(result=>{
    //   console.log("User's existed data",result);
    // })
    this.userService.createuser(data).subscribe(userdata=>{
      console.log("User Created",userdata);
    })
    
  }
  get email_validate(){
    return this.registerFormGroup.get('email')
  }
  get name_validate(){
    return this.registerFormGroup.get('f_name')
  }
  get user_group_validate(){
    return this.registerFormGroup.get('user_group')
  }
  get password_validate(){
    return this.registerFormGroup.get('password')
  }
  get cpassword_validate(){
    return this.registerFormGroup.get('cpassword')
  }
  
}