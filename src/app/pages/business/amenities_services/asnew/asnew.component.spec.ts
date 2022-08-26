import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsnewComponent } from './asnew.component';

describe('AsnewComponent', () => {
  let component: AsnewComponent;
  let fixture: ComponentFixture<AsnewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AsnewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AsnewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
