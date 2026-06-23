export interface CarSpecs {
  horsepower: number;
  torque: string;
  acceleration: string;
  topSpeed: string;
  rangeOrMileage: string;
  batteryCapacity?: string;
  engine: string;
  seating: number;
  cargoVolume: string;
}

export interface Car {
  id: string;
  brand: string;
  model: string;
  year: number;
  price: number; // in USD
  bodyType: 'Sedan' | 'SUV' | 'Hatchback' | 'Coupe' | 'Supercar';
  fuelType: 'Electric' | 'Hybrid' | 'Petrol' | 'Diesel';
  transmission: 'Automatic' | 'Manual' | 'Single-speed';
  drivetrain: 'AWD' | 'RWD' | 'FWD';
  specs: CarSpecs;
  features: string[];
  description: string;
  imageColor: string; // Used to style a premium animated abstract rendering of the car
}

export const BRANDS = [
  'Tesla',
  'Porsche',
  'BMW',
  'Mercedes-Benz',
  'Audi',
  'Ford',
  'Toyota',
  'Hyundai'
];

export const CARS: Car[] = [
  {
    id: 'tesla-model-s-plaid',
    brand: 'Tesla',
    model: 'Model S Plaid',
    year: 2026,
    price: 89990,
    bodyType: 'Sedan',
    fuelType: 'Electric',
    transmission: 'Single-speed',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #e50914, #9b0000)',
    specs: {
      horsepower: 1020,
      torque: '1,020 lb-ft',
      acceleration: '1.99s (0-60 mph)',
      topSpeed: '200 mph',
      rangeOrMileage: '396 miles (EPA est.)',
      batteryCapacity: '100 kWh',
      engine: 'Tri-Motor Permanent Magnet AC',
      seating: 5,
      cargoVolume: '25.0 cu ft'
    },
    features: [
      'Full Self-Driving Capability',
      'Yoke Steering Option',
      '17-inch Cinematic Center Display',
      'Tri-zone Climate Control',
      '22-Speaker Premium Audio'
    ],
    description: 'The Tesla Model S Plaid is the quickest accelerating car in production today. With tri-motor all-wheel drive, it delivers instant torque and supercar-level performance wrapped in a practical, luxurious sedan.'
  },
  {
    id: 'porsche-taycan-turbo-s',
    brand: 'Porsche',
    model: 'Taycan Turbo S',
    year: 2026,
    price: 194900,
    bodyType: 'Sedan',
    fuelType: 'Electric',
    transmission: 'Single-speed',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #0d1b2a, #1b4965)',
    specs: {
      horsepower: 938,
      torque: '818 lb-ft',
      acceleration: '2.3s (0-60 mph)',
      topSpeed: '161 mph',
      rangeOrMileage: '318 miles',
      batteryCapacity: '105 kWh',
      engine: 'Dual Permanent Magnet Motors',
      seating: 4,
      cargoVolume: '14.3 cu ft'
    },
    features: [
      'Porsche Active Ride Suspension',
      '800-volt Architecture (Fast Charging)',
      '16.8-inch Curved Instrument Display',
      'Burmester 3D Surround Sound',
      'Rear Axle Steering'
    ],
    description: 'Porsche Taycan Turbo S represents the pinnacle of electric sports sedan engineering, blending breathtaking speed, race-track handling dynamics, and quintessential Porsche luxury.'
  },
  {
    id: 'porsche-911-gt3-rs',
    brand: 'Porsche',
    model: '911 GT3 RS (992)',
    year: 2025,
    price: 241300,
    bodyType: 'Supercar',
    fuelType: 'Petrol',
    transmission: 'Automatic',
    drivetrain: 'RWD',
    imageColor: 'linear-gradient(135deg, #38b000, #007200)',
    specs: {
      horsepower: 518,
      torque: '342 lb-ft',
      acceleration: '3.0s (0-60 mph)',
      topSpeed: '184 mph',
      rangeOrMileage: '16 mpg combined',
      engine: '4.0L Naturally Aspirated Flat-6',
      seating: 2,
      cargoVolume: '4.6 cu ft'
    },
    features: [
      'Drag Reduction System (DRS)',
      'Carbon Fiber Monocoque Components',
      'Adjustable Dampers from Steering Wheel',
      'Michelin Pilot Sport Cup 2 R Tires',
      'Alcantara Track Steering'
    ],
    description: 'A street-legal track weapon. The Porsche 911 GT3 RS features an advanced aerodynamic concept with a massive active rear wing and a high-revving naturally aspirated flat-six engine.'
  },
  {
    id: 'bmw-m5-competition',
    brand: 'BMW',
    model: 'M5 Competition',
    year: 2026,
    price: 119500,
    bodyType: 'Sedan',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #1d3557, #457b9d)',
    specs: {
      horsepower: 717,
      torque: '737 lb-ft',
      acceleration: '3.4s (0-60 mph)',
      topSpeed: '190 mph',
      rangeOrMileage: '25 miles (Electric) / 22 mpg',
      batteryCapacity: '18.6 kWh',
      engine: '4.4L TwinPower Turbo V8 Plug-in Hybrid',
      seating: 5,
      cargoVolume: '16.4 cu ft'
    },
    features: [
      'M xDrive with 2WD Drift Mode',
      'BMW Curved Display with OS 8.5',
      'Carbon Fiber Roof',
      'Adaptive M Suspension Professional',
      'Harman Kardon Surround Sound System'
    ],
    description: 'The BMW M5 Competition combines plug-in hybrid electrification with a legendary twin-turbo V8, presenting high-performance sports car dynamics alongside business-class comfort.'
  },
  {
    id: 'mercedes-amg-g63',
    brand: 'Mercedes-Benz',
    model: 'AMG G 63',
    year: 2026,
    price: 183000,
    bodyType: 'SUV',
    fuelType: 'Petrol',
    transmission: 'Automatic',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #2b2d42, #14151f)',
    specs: {
      horsepower: 577,
      torque: '627 lb-ft',
      acceleration: '4.2s (0-60 mph)',
      topSpeed: '149 mph',
      rangeOrMileage: '14 mpg combined',
      engine: '4.0L Twin-Turbo V8 with Mild Hybrid',
      seating: 5,
      cargoVolume: '38.1 cu ft'
    },
    features: [
      'Triple Locking Differentials',
      'AMG RIDE CONTROL Suspension',
      'AMG Night Package',
      'Dual 12.3-inch Screens',
      'Burmester Surround Sound'
    ],
    description: 'The AMG G 63 (G-Wagon) is an automotive icon, marrying raw off-road power from its handcrafted biturbo V8 with timeless military styling and ultra-premium cabin comfort.'
  },
  {
    id: 'audi-rs-e-tron-gt',
    brand: 'Audi',
    model: 'RS e-tron GT',
    year: 2026,
    price: 147500,
    bodyType: 'Sedan',
    fuelType: 'Electric',
    transmission: 'Single-speed',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #6c757d, #343a40)',
    specs: {
      horsepower: 637,
      torque: '612 lb-ft',
      acceleration: '3.1s (0-60 mph)',
      topSpeed: '155 mph',
      rangeOrMileage: '249 miles',
      batteryCapacity: '93 kWh',
      engine: 'Dual Synchronous Electric Motors',
      seating: 5,
      cargoVolume: '12.9 cu ft'
    },
    features: [
      'quattro All-Wheel Drive',
      'Adaptive Air Suspension',
      'Matrix Design LED Headlights',
      'Carbon Fiber Interior Inlays',
      'e-tron Sport Sound Synthesizer'
    ],
    description: 'Audi’s flagship electric grand tourer. The RS e-tron GT delivers rapid charging, striking aesthetic lines, and a smooth, futuristic driving experience with sports car handling.'
  },
  {
    id: 'ford-mustang-mach-e-gt',
    brand: 'Ford',
    model: 'Mustang Mach-E GT',
    year: 2025,
    price: 59995,
    bodyType: 'SUV',
    fuelType: 'Electric',
    transmission: 'Single-speed',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #00b4d8, #0077b6)',
    specs: {
      horsepower: 480,
      torque: '634 lb-ft',
      acceleration: '3.5s (0-60 mph)',
      topSpeed: '124 mph',
      rangeOrMileage: '280 miles',
      batteryCapacity: '91 kWh',
      engine: 'Dual Electric Motors',
      seating: 5,
      cargoVolume: '29.7 cu ft'
    },
    features: [
      'MagneRide Damping System',
      'Ford BlueCruise Hands-Free Driving',
      '15.5-inch Vertical Touchscreen',
      'Panoramic Fixed-Glass Roof',
      'B&O Sound System by Bang & Olufsen'
    ],
    description: 'The Ford Mustang Mach-E GT is an all-electric SUV that pays homage to the legendary muscle car with exhilarating acceleration, sharp styling, and advanced driver-assist tech.'
  },
  {
    id: 'toyota-rav4-prime',
    brand: 'Toyota',
    model: 'RAV4 Prime XSE',
    year: 2025,
    price: 48560,
    bodyType: 'SUV',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #d62246, #7b0d1e)',
    specs: {
      horsepower: 302,
      torque: '165 lb-ft (Engine) + Electric Motors',
      acceleration: '5.7s (0-60 mph)',
      topSpeed: '117 mph',
      rangeOrMileage: '42 miles electric / 38 mpg combined',
      batteryCapacity: '18.1 kWh',
      engine: '2.5L 4-Cylinder Plug-in Hybrid',
      seating: 5,
      cargoVolume: '33.5 cu ft'
    },
    features: [
      'Toyota Safety Sense 2.5+',
      '10.5-inch Multimedia Display',
      'Heated and Ventilated Front Seats',
      'JBL Premium Audio System',
      '120V/1500W AC Power Outlet'
    ],
    description: 'The RAV4 Prime is the ultimate hybrid utility vehicle, combining quick acceleration (Toyota’s second fastest vehicle behind the Supra) with 42 miles of pure electric driving range.'
  },
  {
    id: 'hyundai-ioniq-5-n',
    brand: 'Hyundai',
    model: 'Ioniq 5 N',
    year: 2026,
    price: 66100,
    bodyType: 'SUV',
    fuelType: 'Electric',
    transmission: 'Single-speed',
    drivetrain: 'AWD',
    imageColor: 'linear-gradient(135deg, #4895ef, #3f37c9)',
    specs: {
      horsepower: 641,
      torque: '545 lb-ft',
      acceleration: '3.2s (0-60 mph)',
      topSpeed: '162 mph',
      rangeOrMileage: '221 miles',
      batteryCapacity: '84 kWh',
      engine: 'Dual High-Performance Electric Motors',
      seating: 5,
      cargoVolume: '27.2 cu ft'
    },
    features: [
      'N Grin Boost & N Drift Optimizer',
      'Virtual Gearshift System (N e-shift)',
      'N Active Sound+ (Simulated ICE engine)',
      'Electronically Controlled Suspension',
      'Track State of Charge Optimizer'
    ],
    description: 'An track-oriented electric SUV. The Ioniq 5 N is engineered to deliver visceral feedback like a traditional performance car, with virtual shifts, engine soundtrack, and incredible track capabilities.'
  }
];
