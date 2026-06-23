import React, { useState } from 'react';
import { CARS } from './data/cars';
import type { Car } from './data/cars';
import { FilterBar } from './components/FilterBar';
import { CarCard } from './components/CarCard';
import { CarDetails } from './components/CarDetails';
import { CompareDrawer } from './components/CompareDrawer';
import { CompareModal } from './components/CompareModal';
import './App.css';

interface FilterState {
  search: string;
  brand: string;
  bodyType: string;
  fuelType: string;
  maxPrice: number;
}

export const App: React.FC = () => {
  // Find price bounds from dataset
  const prices = CARS.map(c => c.price);
  const minPriceLimit = Math.min(...prices);
  const maxPriceLimit = Math.max(...prices);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    brand: '',
    bodyType: '',
    fuelType: '',
    maxPrice: maxPriceLimit
  });

  // Modal & Drawer State
  const [selectedCar, setSelectedCar] = useState<Car | null>(null);
  const [compareList, setCompareList] = useState<Car[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState<boolean>(false);

  // Handle filter changes
  const handleFilterChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  // Toggle car in compare list
  const handleToggleCompare = (car: Car) => {
    setCompareList(prev => {
      const exists = prev.some(c => c.id === car.id);
      if (exists) {
        return prev.filter(c => c.id !== car.id);
      } else {
        if (prev.length >= 3) return prev; // limit to 3
        return [...prev, car];
      }
    });
  };

  // Remove single car from comparison
  const handleRemoveCompareCar = (car: Car) => {
    setCompareList(prev => prev.filter(c => c.id !== car.id));
  };

  // Clear comparison list
  const handleClearCompare = () => {
    setCompareList([]);
  };

  // Filter logic
  const filteredCars = CARS.filter(car => {
    const searchMatch =
      car.model.toLowerCase().includes(filters.search.toLowerCase()) ||
      car.brand.toLowerCase().includes(filters.search.toLowerCase());
    
    const brandMatch = !filters.brand || car.brand === filters.brand;
    const bodyMatch = !filters.bodyType || car.bodyType === filters.bodyType;
    const fuelMatch = !filters.fuelType || car.fuelType === filters.fuelType;
    const priceMatch = car.price <= filters.maxPrice;

    return searchMatch && brandMatch && bodyMatch && fuelMatch && priceMatch;
  });

  return (
    <div className="app-container">
      {/* Header Section */}
      <header className="app-header animate-slide-up">
        <div className="logo-section">
          <h1>
            <span className="logo-icon">⚡</span> DRIVE MATRIX
          </h1>
          <p className="subtitle">Interactive Car Specifications & Comparison Deck</p>
        </div>
        <div className="stats-badge">
          {CARS.length} Elite Vehicles Cataloged
        </div>
      </header>

      {/* Filtering Section */}
      <section className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
        <FilterBar
          filters={filters}
          onFilterChange={handleFilterChange}
          maxPriceLimit={maxPriceLimit}
          minPriceLimit={minPriceLimit}
        />
      </section>

      {/* Grid of Results */}
      <section className="cars-grid-section animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <div className="results-count">
          Showing {filteredCars.length} of {CARS.length} vehicles matching criteria
        </div>

        {filteredCars.length > 0 ? (
          <div className="cars-grid">
            {filteredCars.map(car => (
              <CarCard
                key={car.id}
                car={car}
                onViewDetails={setSelectedCar}
                isInCompare={compareList.some(c => c.id === car.id)}
                onToggleCompare={handleToggleCompare}
                compareCount={compareList.length}
              />
            ))}
          </div>
        ) : (
          <div className="no-results glass">
            <h3>No Vehicles Match Your Criteria</h3>
            <p>Try clearing or modifying your filter values to see more premium models.</p>
            <button 
              className="btn-clear-filters" 
              onClick={() => setFilters({
                search: '',
                brand: '',
                bodyType: '',
                fuelType: '',
                maxPrice: maxPriceLimit
              })}
            >
              Reset All Filters
            </button>
          </div>
        )}
      </section>

      {/* Modal - Details Sheet */}
      {selectedCar && (
        <CarDetails
          car={selectedCar}
          onClose={() => setSelectedCar(null)}
          isInCompare={compareList.some(c => c.id === selectedCar.id)}
          onToggleCompare={handleToggleCompare}
          compareCount={compareList.length}
        />
      )}

      {/* Compare Tray Drawer */}
      <CompareDrawer
        selectedCars={compareList}
        onRemoveCar={handleRemoveCompareCar}
        onClearAll={handleClearCompare}
        onOpenCompare={() => setIsCompareOpen(true)}
      />

      {/* Modal - Compare Matrix */}
      {isCompareOpen && (
        <CompareModal
          selectedCars={compareList}
          onClose={() => setIsCompareOpen(false)}
          onRemoveCar={handleRemoveCompareCar}
        />
      )}
    </div>
  );
};

export default App;
