import { NbMenuItem } from '@nebular/theme';

export const MENU_ITEMS: NbMenuItem[] = [
  {
    title: 'dashboard',
    icon: 'shopping-cart-outline',
    link: '/pages/dashboard',
    home: true,
  },
  {
    title: 'User Management',
    icon:'person-outline',
    children:[
      {
        title: "User's List",
        link: './userlist',
      },
      {
        title: 'Create new User',
        link: './createuser',
      },
    ],
  },
  {
    title: 'Category',
    icon:'list',
    children:[
      {
        title: 'List',
        link: './category/list',
      },
      {
        title: 'Sub-Category',
        link: './subcategory',
      },
    ], 
  },
  {
    title: 'Amenities & Services',
    icon:'',
    children:[
      {
        title: 'List',
        link: './amenities&services/list',
      },
      {
        title: 'New',
        link: './amenities&services/new',
      },
    ], 
  },
  {
    title: 'Business',
    icon:'',
    children:[
      {
        title: 'List',
        link: './business/list',
      },
      {
        title: 'New',
        link: './business/new',
      },
    ], 
  },
 
 
  
];
