import { NgModule } from '@angular/core';
import { NbButtonModule, NbCardModule, NbMenuModule } from '@nebular/theme';

import { ThemeModule } from '../@theme/theme.module';
import { PagesComponent } from './pages.component';
import { DashboardModule } from './dashboard/dashboard.module';
import { ECommerceModule } from './e-commerce/e-commerce.module';
import { PagesRoutingModule } from './pages-routing.module';
import { MiscellaneousModule } from './miscellaneous/miscellaneous.module';
import { CategorylistComponent } from './category/categorylist/categorylist.component';
import { BusinesslistComponent } from './business/businesslist/businesslist.component';
import { BusinessnewComponent } from './business/businessnew/businessnew.component';
import { AslistComponent } from './business/amenities_services/aslist/aslist.component';
import { AsnewComponent } from './business/amenities_services/asnew/asnew.component';
import { Ng2SmartTableModule } from 'ng2-smart-table';
import { SubcategoryComponent } from './category/subcategory/subcategory.component';
// import { LoginComponent } from './auth/login/login.component';
import { ReactiveFormsModule } from '@angular/forms';
import { UsermanagementComponent } from './usermanagement/usermanagement.component';
import { UserlistComponent } from './usermanagement/userlist/userlist.component';

@NgModule({
  imports: [
    PagesRoutingModule,
    ThemeModule,
    NbMenuModule,
    DashboardModule,
    ECommerceModule,
    MiscellaneousModule,
    NbCardModule,
    Ng2SmartTableModule,
    NbButtonModule,
    ReactiveFormsModule,
  ],
  declarations: [
    PagesComponent,
    CategorylistComponent,
    BusinesslistComponent,
    BusinessnewComponent,
    AslistComponent,
    AsnewComponent,
    SubcategoryComponent,
    UsermanagementComponent,
    UserlistComponent,
    // LoginComponent,
  ],
})
export class PagesModule {
}
