import React, { Component } from 'react';
import axios from 'axios';
import "./ButtonModal.css";
import "./CarSearchResults.css";

class CarSearchResults extends Component {
  constructor(props) {
    super(props);
    this.state = {
      cars: [],
      has_next_page: true,
      cursor: 0,
      isLoading: true

    }
  }

  componentDidMount() {
    this.fetchCars(this.state.cursor);
  }

  componentDidUpdate(prevProps) {
    if (Object.keys(prevProps).some(key => prevProps[key] !== this.props[key])) {
      this.fetchCars(0);
    }
  }

  handlePrevClick = () => {
    const { cursor } = this.state;
    this.fetchCars(cursor - 1);
  }

  handleNextClick = () => {
    const { cursor } = this.state;
    this.fetchCars(cursor + 1);
  }

  fetchCars = (cursor) => {
    const {
        brand,
        model,
        minYear,
        maxYear,
        fuel_type,
        body_type,
        show_bitten_cars,
        show_good_price,
        minPrice,
        maxPrice,
        minHorsePower,
        maxHorsePower,
        minMileage,
        maxMileage
    } = this.props;

    this.setState({ isLoading: true });

    // выполняем запрос на сервер для получения списка машин
    axios.get(`http://127.0.0.1:5050/cars/search?brand=${brand}&model=${model}&min_year=${minYear}&max_year=${maxYear}&fuel_type=${fuel_type}&body_type=${body_type}&show_bitten_cars=${show_bitten_cars}&show_good_price=${show_good_price}&min_price=${minPrice}&max_price=${maxPrice}&min_horse_power=${minHorsePower}&max_horse_power=${maxHorsePower}&min_mileage=${minMileage}&max_mileage=${maxMileage}&cursor=${cursor}`)
      .then(response => {
        if (response.data.results.length === 0) {
          this.setState({ cars: [], has_next_page: response.data.has_next_page, cursor, isLoading: false });
        } else {
          this.setState({ cars: response.data.results, has_next_page: response.data.has_next_page, cursor, isLoading: false });
        }
      });
  }

  render() {
    const { cars, has_next_page, cursor, isLoading } = this.state;

    if (isLoading) {
      return <div>Загрузка...</div>;
    }

    if (cars.length === 0) {
      return <div>УПС! Ничего не найдено</div>;
    }

    return (
      <div class="car-table">
		<ul class="s3">
          {cars.map(car => (
            <li><a href={car.link} class="link" rel="noopener noreferrer" target="_blank"><ul class="tab-content" key={car.id}>
			  <li> Название: {car.brand} {car.model} </li> 
			  <li> Вид кузова: {car.body_type}</li>
			  <li> Вид топлива: {car.fuel_type}</li> 
			  <li> Привод: {car.transmission}</li> 
			  <li> Двигатель: {car.engine}</li> 
			  <li> Год выпуска: {car.year}</li> 
			  <li> Цена обьявления: {car.price}</li> 
			  <li> Пробег: {car.mileage}</li> 
			  <li> Битая: {car.is_bitten}</li> 
        <li> Реальная цена: {car.predicted_price} </li>
			</ul></a></li>
              ))}
			  </ul>

        <button class="button-slider" onClick={this.handlePrevClick} disabled={cursor <= 0}>Предыдущая страница</button>
        <button class="button-slider" onClick={this.handleNextClick} disabled={!has_next_page}>Следующая страница</button>
      </div>
    );
  }
}
      
export default CarSearchResults;
