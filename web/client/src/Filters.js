import React, { Component } from 'react';
import axios from 'axios';
import CarSearchResults from './CarSearchResults';
import ButtonModal from './ButtonModal';
import "./Checkbox.css";
import "./Filters.css";
import "./Select.css";

class CarSearch extends Component {
  constructor(props) {
    super(props);
    this.state = {
      brands: [],
      models: [],
      fuel_types: [], 
      body_types: [],
      selectedBrand: null,
      selectedModel: null,
      selectedFuelType: null,
      selectedBodyType: null,
      minYear: null,
      maxYear: null,
      minHorsePower: null,
      maxHorsePower: null,
      minMileage: null,
      maxMileage: null,
      minPrice: null,
      maxPrice: null,
      showBittenCars: false,
    }
  }

  componentDidMount() {
    axios.get('http://127.0.0.1:5000/brand/list')
      .then(response => {
        this.setState({ brands: response.data });
      });

    axios.get('http://127.0.0.1:5000/fuel-type/list')
      .then(response => {
        this.setState({ fuel_types: response.data });
      });

    axios.get('http://127.0.0.1:5000/body-type/list')
      .then(response => {
        this.setState({ body_types: response.data });
      });
  }

  handleBrandChange = (event) => {
    const selectedBrand = event.target.value;
    this.setState({ selectedBrand, selectedModel: null, models: [] });
    axios.get(`http://127.0.0.1:5000/model/list?brand=${selectedBrand}`)
    .then(response => {
      this.setState({ models: response.data });
    });
  }

  handleModelChange = (event) => {
    this.setState({ selectedModel: event.target.value });
  }

  handleFuelTypeChange = (event) => {
    this.setState({ selectedFuelType: event.target.value });
  }

  handleBodyTypeChange = (event) => {
    this.setState({ selectedBodyType: event.target.value });
  }

  handleTestChange = (event) => {
    this.setState({ test: event.target.value });
  }

  handleMinYearChange = (event) => {
    this.setState({ minYear: event.target.value });
  }

  handleMaxYearChange = (event) => {
    this.setState({ maxYear: event.target.value });
  }

  handleMinPriceChange = (event) => {
    this.setState({ minPrice: event.target.value });
  }

  handleMaxPriceChange = (event) => {
    this.setState({ maxPrice: event.target.value });
  }

  handleMinHorsePowerChange = (event) => {
    this.setState({ minHorsePower: event.target.value });
  }

  handleMaxHorsePowerChange = (event) => {
    this.setState({ maxHorsePower: event.target.value });
  }

  handleMinMileageChange = (event) => {
    this.setState({ minMileage: event.target.value });
  }

  handleMaxMileageChange = (event) => {
    this.setState({ maxMileage: event.target.value });
  }

  handleShowBittenChange = () => {
    this.setState({ showBittenCars: !this.showBittenCars });
  }

  render() {
    const {
      brands,
      models,
      fuel_types,
      body_types,
      selectedBrand,
      selectedModel,
      selectedFuelType,
      selectedBodyType,
      showBittenCars,
      minYear,
      maxYear,
      minHorsePower,
      maxHorsePower,
      minMileage,
      maxMileage,
      minPrice,
      maxPrice,
    } = this.state;

    return (
      <div class="container">
        <div class="left-column">
          <select value={selectedBrand} onChange={this.handleBrandChange}>
            <option value="" >Выбрать марку машины</option>
            {brands.map(brand => (
              <option key={brand.id} value={brand.name}>{brand.name}</option>
            ))}
          </select>

          <select value={selectedModel} onChange={this.handleModelChange} disabled={!selectedBrand}>
            <option value="">Выбрать модель машины</option>
            {models.map(model => (
              <option key={model.id} value={model.name}>{model.name}</option>
            ))}
          </select>

          <select value={selectedFuelType} onChange={this.handleFuelTypeChange} >
            <option value="">Выбрать тип двигателя</option>
            {fuel_types.map(fuel_type => (
              <option key={fuel_type} value={fuel_type}>{fuel_type}</option>
            ))}
          </select>

          <select value={selectedBodyType} onChange={this.handleBodyTypeChange} >
            <option value="">Выбрать тип кузова</option>
            {body_types.map(body_type => (
              <option key={body_type} value={body_type}>{body_type}</option>
            ))}
          </select>

          <ButtonModal
            buttonText="Год выпуска"
            handleMinChange={this.handleMinYearChange}
            handleMaxChange={this.handleMaxYearChange}
            className="modal"/>

          <ButtonModal
            buttonText="Кол-во лошадиных сил"
            handleMinChange={this.handleMinHorsePowerChange}
            handleMaxChange={this.handleMaxHorsePowerChange}
            className="modal"/>

          <ButtonModal
            buttonText="Пробег"
            handleMinChange={this.handleMinMileageChange}
            handleMaxChange={this.handleMaxMileageChange}
            className="modal"/>

          <ButtonModal
            buttonText="Цена"
            handleMinChange={this.handleMinPriceChange}
            handleMaxChange={this.handleMaxPriceChange}
            className="modal"/>

          <div class="switch">
            <input
            id="checkbox-id"
            class="checkbox-input checkbox-input-yes-no"
            type="checkbox"
            onChange={this.handleShowBittenChange}/>

            <label
            for="checkbox-id"
            data-on="Показывать битые машины"
            data-off="Не показывать битые машины"/>
          </div>
        </div>

        <div class="right-column">
          <h1>Результаты поиска:</h1>
          <CarSearchResults
            brand={selectedBrand}
            model={selectedModel}
            minYear={minYear}
            maxYear={maxYear}
            fuel_type={selectedFuelType}
            body_type={selectedBodyType}
            show_bitten_cars={showBittenCars}
            minPrice={minPrice}
            maxPrice={maxPrice}
            minHorsePower={minHorsePower} 
            maxHorsePower={maxHorsePower}
            minMileage={minMileage}
            maxMileage={maxMileage}/>
        </div>
      </div>
    );
  }
}

export default CarSearch;

