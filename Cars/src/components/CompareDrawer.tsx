import React from 'react';
import type { Car } from '../data/cars';

interface CompareDrawerProps {
  selectedCars: Car[];
  onRemoveCar: (car: Car) => void;
  onClearAll: () => void;
  onOpenCompare: () => void;
}

export const CompareDrawer: React.FC<CompareDrawerProps> = ({
  selectedCars,
  onRemoveCar,
  onClearAll,
  onOpenCompare
}) => {
  if (selectedCars.length === 0) return null;

  return (
    <div className="compare-drawer-wrapper animate-slide-up">
      <div className="compare-drawer glass">
        <div className="drawer-info">
          <h4>Compare Cars</h4>
          <span className="drawer-counter">{selectedCars.length} of 3 selected</span>
        </div>

        <div className="drawer-items">
          {selectedCars.map(car => (
            <div key={car.id} className="drawer-item glass">
              <div className="drawer-item-color" style={{ background: car.imageColor }} />
              <div className="drawer-item-details">
                <span className="item-brand">{car.brand}</span>
                <span className="item-model">{car.model}</span>
              </div>
              <button 
                className="btn-remove-item" 
                onClick={() => onRemoveCar(car)}
                aria-label={`Remove ${car.model} from comparison`}
              >
                &times;
              </button>
            </div>
          ))}
          {Array.from({ length: 3 - selectedCars.length }).map((_, idx) => (
            <div key={idx} className="drawer-item-placeholder">
              <span>+ Add Car</span>
            </div>
          ))}
        </div>

        <div className="drawer-actions">
          <button className="btn-clear-all" onClick={onClearAll}>
            Clear All
          </button>
          
          <button 
            className="btn-compare-now" 
            onClick={onOpenCompare}
            disabled={selectedCars.length < 2}
            title={selectedCars.length < 2 ? "Select at least 2 cars to compare" : "Open comparison matrix"}
          >
            Compare Now
          </button>
        </div>
      </div>
    </div>
  );
};
