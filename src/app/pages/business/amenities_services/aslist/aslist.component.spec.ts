import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AslistComponent } from './aslist.component';

describe('AslistComponent', () => {
  let component: AslistComponent;
  let fixture: ComponentFixture<AslistComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AslistComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AslistComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
