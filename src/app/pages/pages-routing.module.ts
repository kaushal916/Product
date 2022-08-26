import { RouterModule, Routes } from '@angular/router';
import { NgModule } from '@angular/core';
import { PagesComponent } from './pages.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ECommerceComponent } from './e-commerce/e-commerce.component';
import { NotFoundComponent } from './miscellaneous/not-found/not-found.component';
import { CategorylistComponent } from './category/categorylist/categorylist.component';
import { AslistComponent } from './business/amenities_services/aslist/aslist.component';
import { AsnewComponent } from './business/amenities_services/asnew/asnew.component';
import { BusinesslistComponent } from './business/businesslist/businesslist.component';
import { BusinessnewComponent } from './business/businessnew/businessnew.component';
import { SubcategoryComponent } from './category/subcategory/subcategory.component';
import { UsermanagementComponent } from './usermanagement/usermanagement.component';
import { UserlistComponent } from './usermanagement/userlist/userlist.component';
import { AuthGuard } from '../authguard/auth.guard';
// import { LoginComponent } from './auth/login/login.component';

const routes: Routes = [{
  path: '',
  component: PagesComponent,
  children: [
    {
      path: 'dashboard',
      component: ECommerceComponent,
      canActivate:[AuthGuard]
    },
    { path:'category/list', component:CategorylistComponent,canActivate:[AuthGuard]},
    { path:'subcategory', component:SubcategoryComponent,canActivate:[AuthGuard]},
    { path:'amenities&services/list', component:AslistComponent,canActivate:[AuthGuard]},
    { path:'amenities&services/new', component:AsnewComponent,canActivate:[AuthGuard]},
    { path:'business/list', component:BusinesslistComponent,canActivate:[AuthGuard]},
    { path:'business/new', component:BusinessnewComponent,canActivate:[AuthGuard]},
    { path:'createuser', component:UsermanagementComponent,canActivate:[AuthGuard]},
    { path:'userlist',component:UserlistComponent,canActivate:[AuthGuard]},
    {
      path: '',
      redirectTo: 'dashboard',
      pathMatch: 'full',
    },
    {
      path: '**',
      component: NotFoundComponent,
    },
  ],
}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PagesRoutingModule {
}
