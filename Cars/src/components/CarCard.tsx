import React from 'react';
import type { Car } from '../data/cars';

interface CarCardProps {
  car: Car;
  onViewDetails: (car: Car) => void;
  isInCompare: boolean;
  onToggleCompare: (car: Car) => void;
  compareCount: number;
}

export const CarCard: React.FC<CarCardProps> = ({
  car,
  onViewDetails,
  isInCompare,
  onToggleCompare,
  compareCount
}) => {
  const isCompareDisabled = !isInCompare && compareCount >= 3;

  return (
    <div className="car-card glass-interactive">
      {/* Visual Car Graphic Container */}
      <div 
        className="car-image-container" 
        style={{ background: car.imageColor }}
      >
        <div className="car-image-shine" />
        <div className="car-brand-badge">{car.brand}</div>
        <div className="car-visual-silhouette">
          {/* Abstract representation of a premium car structure using CSS shapes/lines */}
          <div className="car-glow-ring" />
          <div className="car-body-line" />
          <div className="car-wheel-left" />
          <div className="car-wheel-right" />
        </div>
        <div className="car-year">{car.year}</div>
      </div>

      {/* Car Content Info */}
      <div className="car-info">
        <div className="car-header">
          <h3 className="car-title">{car.model}</h3>
          <span className="car-price">${car.price.toLocaleString()}</span>
        </div>

        <p className="car-desc-short">{car.description.substring(0, 80)}...</p>

        {/* Quick Specs Grid */}
        <div className="quick-specs-grid">
          <div className="quick-spec-item">
            <span className="spec-label">Power</span>
            <span className="spec-val">{car.specs.horsepower} HP</span>
          </div>
          <div className="quick-spec-item">
            <span className="spec-label">0-60 mph</span>
            <span className="spec-val">{car.specs.acceleration.split(' ')[0]}</span>
          </div>
          <div className="quick-spec-item">
            <span className="spec-label">Type</span>
            <span className="spec-val">{car.fuelType}</span>
          </div>
          <div className="quick-spec-item">
            <span className="spec-label">Body</span>
            <span className="spec-val">{car.bodyType}</span>
          </div>
        </div>

        {/* Card Actions */}
        <div className="car-actions">
          <button 
            className="btn-view-details" 
            onClick={() => onViewDetails(car)}
          >
            Specs & Details
          </button>
          
          <button 
            className={`btn-compare-toggle ${isInCompare ? 'active' : ''}`}
            onClick={() => onToggleCompare(car)}
            disabled={isCompareDisabled}
            title={isCompareDisabled ? "Max 3 cars for comparison" : "Compare this car"}
          >
            {isInCompare ? (
              <>
                <span className="compare-dot active-dot" />
                Comparing
              </>
            ) : (
              <>
                <span className="compare-dot" />
                Compare
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
