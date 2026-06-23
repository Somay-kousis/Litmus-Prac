import React from 'react';
import { BRANDS } from '../data/cars';

interface FilterState {
  search: string;
  brand: string;
  bodyType: string;
  fuelType: string;
  maxPrice: number;
}

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  maxPriceLimit: number;
  minPriceLimit: number;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFilterChange,
  maxPriceLimit,
  minPriceLimit
}) => {
  const handleChange = (key: keyof FilterState, value: any) => {
    onFilterChange({
      ...filters,
      [key]: value
    });
  };

  const handleClear = () => {
    onFilterChange({
      search: '',
      brand: '',
      bodyType: '',
      fuelType: '',
      maxPrice: maxPriceLimit
    });
  };

  const bodyTypes = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Supercar'];
  const fuelTypes = ['Electric', 'Hybrid', 'Petrol', 'Diesel'];

  return (
    <div className="filter-bar glass">
      <div className="filter-grid">
        {/* Search */}
        <div className="filter-item search-box">
          <label htmlFor="search-input">Search Cars</label>
          <input
            id="search-input"
            type="text"
            placeholder="Search by model, brand..."
            value={filters.search}
            onChange={(e) => handleChange('search', e.target.value)}
            className="filter-input"
          />
        </div>

        {/* Brand */}
        <div className="filter-item">
          <label htmlFor="brand-select">Brand</label>
          <select
            id="brand-select"
            value={filters.brand}
            onChange={(e) => handleChange('brand', e.target.value)}
            className="filter-select"
          >
            <option value="">All Brands</option>
            {BRANDS.map(brand => (
              <option key={brand} value={brand}>{brand}</option>
            ))}
          </select>
        </div>

        {/* Body Type */}
        <div className="filter-item">
          <label htmlFor="body-select">Body Type</label>
          <select
            id="body-select"
            value={filters.bodyType}
            onChange={(e) => handleChange('bodyType', e.target.value)}
            className="filter-select"
          >
            <option value="">All Body Types</option>
            {bodyTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* Fuel Type */}
        <div className="filter-item">
          <label htmlFor="fuel-select">Fuel / Power</label>
          <select
            id="fuel-select"
            value={filters.fuelType}
            onChange={(e) => handleChange('fuelType', e.target.value)}
            className="filter-select"
          >
            <option value="">All Fuel Types</option>
            {fuelTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        {/* Price Slider */}
        <div className="filter-item price-range">
          <div className="price-range-labels">
            <label htmlFor="price-slider">Max Price</label>
            <span className="price-display">${filters.maxPrice.toLocaleString()}</span>
          </div>
          <input
            id="price-slider"
            type="range"
            min={minPriceLimit}
            max={maxPriceLimit}
            step={5000}
            value={filters.maxPrice}
            onChange={(e) => handleChange('maxPrice', parseInt(e.target.value))}
            className="filter-slider"
          />
          <div className="slider-limits">
            <span>${minPriceLimit.toLocaleString()}</span>
            <span>${maxPriceLimit.toLocaleString()}</span>
          </div>
        </div>

        {/* Reset */}
        <div className="filter-item filter-actions">
          <button onClick={handleClear} className="btn-clear-filters">
            Reset Filters
          </button>
        </div>
      </div>
    </div>
  );
};
