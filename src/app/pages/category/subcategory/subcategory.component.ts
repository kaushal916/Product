import { Component, OnInit } from '@angular/core';

import { LocalDataSource } from 'ng2-smart-table';

@Component({
  selector: 'ngx-subcategory',
  templateUrl: './subcategory.component.html',
  styleUrls: ['./subcategory.component.scss']
})
export class SubcategoryComponent implements OnInit {
  settings = {
    add: {
      addButtonContent: '<i class="nb-plus"></i>',
      createButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
    },
    edit: {
      editButtonContent: '<i class="nb-edit"></i>',
      saveButtonContent: '<i class="nb-checkmark"></i>',
      cancelButtonContent: '<i class="nb-close"></i>',
    },
    delete: {
      deleteButtonContent: '<i class="nb-trash"></i>',
      confirmDelete: true,
    },
    columns: {
      id: {
        title: 'ID',
        type: 'number',
      },
      Name: {
        title: 'Name',
        type: 'string',
      },
      Category: {
        title: 'Category',
        type: 'string'
      },
      status: {
        title: 'Status',
        type: 'string',
      },
    },
  };
source: LocalDataSource = new LocalDataSource();

constructor() { }

onDeleteConfirm(event):void{
  if (window.confirm('Are you sure you want to delete?')) {
    event.confirm.resolve()
  }else{
    event.confirm.reject()
  }
}


  ngOnInit(): void {
  }

}
