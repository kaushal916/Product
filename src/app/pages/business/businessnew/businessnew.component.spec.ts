import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BusinessnewComponent } from './businessnew.component';

describe('BusinessnewComponent', () => {
  let component: BusinessnewComponent;
  let fixture: ComponentFixture<BusinessnewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BusinessnewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BusinessnewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
