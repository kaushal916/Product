import { Component, OnInit } from '@angular/core';
import { LocalDataSource } from 'ng2-smart-table';
import { UserService } from '../../../services/user.service';



@Component({
  selector: 'ngx-categorylist',
  templateUrl: './categorylist.component.html',
  styleUrls: ['./categorylist.component.scss']
})
export class CategorylistComponent implements OnInit {
  
  listcategory:any =[]

 constructor(private userservice:UserService) {
  this.userservice.listcategory().subscribe(data=>{
    this.listcategory = data
  })
  }
  ngOnInit(): void {
    
  }
}
