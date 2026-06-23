import React from 'react';
import type { Car } from '../data/cars';

interface CarDetailsProps {
  car: Car | null;
  onClose: () => void;
  isInCompare: boolean;
  onToggleCompare: (car: Car) => void;
  compareCount: number;
}

export const CarDetails: React.FC<CarDetailsProps> = ({
  car,
  onClose,
  isInCompare,
  onToggleCompare,
  compareCount
}) => {
  if (!car) return null;

  const isCompareDisabled = !isInCompare && compareCount >= 3;

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div className="modal-content glass animate-slide-up" onClick={(e) => e.stopPropagation()}>
        {/* Modal Close */}
        <button className="btn-modal-close" onClick={onClose} aria-label="Close modal">
          &times;
        </button>

        {/* Modal Header banner */}
        <div className="modal-header-hero" style={{ background: car.imageColor }}>
          <div className="modal-hero-shine" />
          <div className="modal-hero-info">
            <span className="modal-tag-year">{car.year}</span>
            <h2 className="modal-title">{car.brand} {car.model}</h2>
            <span className="modal-price">${car.price.toLocaleString()}</span>
          </div>
        </div>

        {/* Modal Body */}
        <div className="modal-body-scroll">
          {/* Description */}
          <div className="modal-section description-sec">
            <h3>Overview</h3>
            <p>{car.description}</p>
          </div>

          {/* Quick Config Specs */}
          <div className="spec-sheets-grid">
            {/* Performance sheet */}
            <div className="spec-sheet-card glass">
              <h4 className="sheet-title">Performance</h4>
              <div className="sheet-row">
                <span className="label">Horsepower</span>
                <span className="val">{car.specs.horsepower} HP</span>
              </div>
              <div className="sheet-row">
                <span className="label">Torque</span>
                <span className="val">{car.specs.torque}</span>
              </div>
              <div className="sheet-row">
                <span className="label">0-60 mph</span>
                <span className="val">{car.specs.acceleration}</span>
              </div>
              <div className="sheet-row">
                <span className="label">Top Speed</span>
                <span className="val">{car.specs.topSpeed}</span>
              </div>
            </div>

            {/* Powertrain & Efficiency sheet */}
            <div className="spec-sheet-card glass">
              <h4 className="sheet-title">Powertrain & Fuel</h4>
              <div className="sheet-row">
                <span className="label">Engine/Motor</span>
                <span className="val">{car.specs.engine}</span>
              </div>
              <div className="sheet-row">
                <span className="label">Transmission</span>
                <span className="val">{car.transmission}</span>
              </div>
              <div className="sheet-row">
                <span className="label">Drivetrain</span>
                <span className="val">{car.drivetrain}</span>
              </div>
              <div className="sheet-row">
                <span className="label">Fuel / Power</span>
                <span className="val">{car.fuelType}</span>
              </div>
            </div>

            {/* Dimensions & Capacity sheet */}
            <div className="spec-sheet-card glass">
              <h4 className="sheet-title">Dimensions & Capacity</h4>
              <div className="sheet-row">
                <span className="label">Range / Mileage</span>
                <span className="val">{car.specs.rangeOrMileage}</span>
              </div>
              {car.specs.batteryCapacity && (
                <div className="sheet-row">
                  <span className="label">Battery Capacity</span>
                  <span className="val">{car.specs.batteryCapacity}</span>
                </div>
              )}
              <div className="sheet-row">
                <span className="label">Seating Capacity</span>
                <span className="val">{car.specs.seating} Seats</span>
              </div>
              <div className="sheet-row">
                <span className="label">Cargo Volume</span>
                <span className="val">{car.specs.cargoVolume}</span>
              </div>
            </div>
          </div>

          {/* Features Highlights */}
          <div className="modal-section features-sec">
            <h3>Premium Features</h3>
            <ul className="features-badge-list">
              {car.features.map((feature, idx) => (
                <li key={idx} className="feature-badge">
                  <span className="badge-bullet">•</span> {feature}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Modal Actions Footer */}
        <div className="modal-footer">
          <button className="btn-modal-secondary" onClick={onClose}>
            Back to Dashboard
          </button>
          
          <button 
            className={`btn-modal-primary ${isInCompare ? 'active' : ''}`}
            onClick={() => onToggleCompare(car)}
            disabled={isCompareDisabled}
          >
            {isInCompare ? 'Remove from Compare' : 'Add to Compare'}
          </button>
        </div>
      </div>
    </div>
  );
};
