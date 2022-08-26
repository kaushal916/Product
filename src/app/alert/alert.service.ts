import { Injectable } from '@angular/core';
import {
  NbGlobalPhysicalPosition,
  NbToastrService,
} from '@nebular/theme';


@Injectable({
  providedIn: 'root'
})
export class AlertService {

  constructor(private toastrservice: NbToastrService) { }
  successalert(title: string,status: string){
    const config = {
      status: status,
      destroyByClick: true,
      duration: 1500,
      hasIcon: true,
      position: NbGlobalPhysicalPosition.TOP_RIGHT,
      preventDuplicates: false,
    };
    // const titleContent = title ? `. ${title}` : '';

    // this.index += 1;
    this.toastrservice.show(
      `Toast `,
      title);
  }
}
