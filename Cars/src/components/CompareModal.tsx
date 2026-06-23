import React from 'react';
import type { Car } from '../data/cars';

interface CompareModalProps {
  selectedCars: Car[];
  onClose: () => void;
  onRemoveCar: (car: Car) => void;
}

export const CompareModal: React.FC<CompareModalProps> = ({
  selectedCars,
  onClose,
  onRemoveCar
}) => {
  if (selectedCars.length === 0) return null;

  // Helper to extract numeric value from acceleration string (e.g. "1.99s (0-60 mph)" -> 1.99)
  const parseAcceleration = (accStr: string): number => {
    const matched = accStr.match(/^[\d.]+/);
    return matched ? parseFloat(matched[0]) : Infinity;
  };

  // Compute best values among the selected cars
  const minPrice = Math.min(...selectedCars.map(c => c.price));
  const maxHorsepower = Math.max(...selectedCars.map(c => c.specs.horsepower));
  const minAcceleration = Math.min(...selectedCars.map(c => parseAcceleration(c.specs.acceleration)));

  return (
    <div className="modal-overlay compare-modal-overlay animate-fade-in" onClick={onClose}>
      <div className="compare-modal-content glass animate-slide-up" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="compare-modal-header">
          <h2>Car Comparison Matrix</h2>
          <button className="btn-modal-close" onClick={onClose}>
            &times;
          </button>
        </div>

        {/* Comparison Grid */}
        <div className="compare-matrix-scroll">
          <table className="compare-table">
            <thead>
              <tr>
                <th className="sticky-col spec-name-col">Specification</th>
                {selectedCars.map(car => (
                  <th key={car.id} className="car-header-col">
                    <div className="compare-car-card">
                      <div className="compare-car-color" style={{ background: car.imageColor }}>
                        <button 
                          className="btn-remove-compare" 
                          onClick={() => onRemoveCar(car)}
                          title="Remove from comparison"
                        >
                          &times;
                        </button>
                      </div>
                      <h3>{car.brand}</h3>
                      <h4>{car.model}</h4>
                      <span className="compare-price">${car.price.toLocaleString()}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Price Row */}
              <tr>
                <td className="sticky-col spec-label-row">Price</td>
                {selectedCars.map(car => {
                  const isBest = car.price === minPrice;
                  return (
                    <td key={car.id} className={isBest ? 'best-value' : ''}>
                      ${car.price.toLocaleString()}
                      {isBest && <span className="winner-badge">★ Lowest Price</span>}
                    </td>
                  );
                })}
              </tr>

              {/* Horsepower Row */}
              <tr>
                <td className="sticky-col spec-label-row">Horsepower</td>
                {selectedCars.map(car => {
                  const isBest = car.specs.horsepower === maxHorsepower;
                  return (
                    <td key={car.id} className={isBest ? 'best-value' : ''}>
                      {car.specs.horsepower} HP
                      {isBest && <span className="winner-badge">★ Highest Power</span>}
                    </td>
                  );
                })}
              </tr>

              {/* Acceleration Row */}
              <tr>
                <td className="sticky-col spec-label-row">0-60 mph Acceleration</td>
                {selectedCars.map(car => {
                  const isBest = parseAcceleration(car.specs.acceleration) === minAcceleration;
                  return (
                    <td key={car.id} className={isBest ? 'best-value' : ''}>
                      {car.specs.acceleration}
                      {isBest && <span className="winner-badge">★ Quickest</span>}
                    </td>
                  );
                })}
              </tr>

              {/* Range/Mileage Row */}
              <tr>
                <td className="sticky-col spec-label-row">Range / Fuel Economy</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.rangeOrMileage}</td>
                ))}
              </tr>

              {/* Fuel/Power Type Row */}
              <tr>
                <td className="sticky-col spec-label-row">Fuel Type</td>
                {selectedCars.map(car => (
                  <td key={car.id}>
                    <span className={`badge-fuel ${car.fuelType.toLowerCase()}`}>
                      {car.fuelType}
                    </span>
                  </td>
                ))}
              </tr>

              {/* Body Type Row */}
              <tr>
                <td className="sticky-col spec-label-row">Body Style</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.bodyType}</td>
                ))}
              </tr>

              {/* Transmission Row */}
              <tr>
                <td className="sticky-col spec-label-row">Transmission</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.transmission}</td>
                ))}
              </tr>

              {/* Drivetrain Row */}
              <tr>
                <td className="sticky-col spec-label-row">Drivetrain</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.drivetrain}</td>
                ))}
              </tr>

              {/* Engine/Motor Row */}
              <tr>
                <td className="sticky-col spec-label-row">Engine Details</td>
                {selectedCars.map(car => (
                  <td key={car.id} className="small-text">{car.specs.engine}</td>
                ))}
              </tr>

              {/* Top Speed Row */}
              <tr>
                <td className="sticky-col spec-label-row">Top Speed</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.topSpeed}</td>
                ))}
              </tr>

              {/* Torque Row */}
              <tr>
                <td className="sticky-col spec-label-row">Torque</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.torque}</td>
                ))}
              </tr>

              {/* Seating Row */}
              <tr>
                <td className="sticky-col spec-label-row">Seating Capacity</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.seating} Passengers</td>
                ))}
              </tr>

              {/* Cargo Volume Row */}
              <tr>
                <td className="sticky-col spec-label-row">Cargo Volume</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.cargoVolume}</td>
                ))}
              </tr>

              {/* Battery Capacity Row */}
              <tr>
                <td className="sticky-col spec-label-row">Battery Capacity</td>
                {selectedCars.map(car => (
                  <td key={car.id}>{car.specs.batteryCapacity || 'N/A'}</td>
                ))}
              </tr>

              {/* Key Features Row */}
              <tr>
                <td className="sticky-col spec-label-row">Highlighted Features</td>
                {selectedCars.map(car => (
                  <td key={car.id}>
                    <ul className="compare-features-list">
                      {car.features.slice(0, 3).map((feat, idx) => (
                        <li key={idx}>{feat}</li>
                      ))}
                    </ul>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        <div className="compare-modal-footer">
          <button className="btn-modal-secondary" onClick={onClose}>
            Close Matrix
          </button>
        </div>
      </div>
    </div>
  );
};
