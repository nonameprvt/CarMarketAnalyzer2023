import React, { Component } from 'react';
import axios from 'axios';
import "./CarSearchResults.css";

class CarSearchResults extends Component {
  constructor(props) {
    super(props);
    this.state = {
      cars: [], // список машин
      has_next_page: true,
      cursor: 0, // положение курсора в списке машин
      isLoading: true // флаг загрузки данных с сервера

    }
  }

  componentDidMount() {
    this.fetchCars(this.state.cursor);
  }

  componentDidUpdate(prevProps) {
    // при обновлении компонента или изменении выбранных марки и модели машин, загружаем первую страницу списка машин
    if (Object.keys(prevProps).some(key => prevProps[key] !== this.props[key])) {
      this.fetchCars(0);
    }
  }

  handlePrevClick = () => {
    const { cursor } = this.state;
    // выполняем запрос на сервер для получения предыдущей страницы списка машин
    this.fetchCars(cursor - 1);
  }

  handleNextClick = () => {
    const { cursor } = this.state;
    // выполняем запрос на сервер для получения следующей страницы списка машин
    this.fetchCars(cursor + 1);
  }

  fetchCars = (cursor) => {
    const { brand, model, minYear, maxYear, fuel_type, body_type, show_bitten_cars, minPrice, maxPrice, minHorsePower, maxHorsePower, minMileage, maxMileage } = this.props;

    this.setState({ isLoading: true });

    // выполняем запрос на сервер для получения списка машин
    axios.get(`http://127.0.0.1:5000/cars/search?brand=${brand}&model=${model}&min_year=${minYear}&max_year=${maxYear}&fuel_type=${fuel_type}&body_type=${body_type}&show_bitten_cars=${show_bitten_cars}&min_price=${minPrice}&max_price=${maxPrice}&min_horse_power=${minHorsePower}&max_horse_power=${maxHorsePower}&min_mileage=${minMileage}&max_mileage=${maxMileage}&cursor=${cursor}`)
      .then(response => {
        if (response.data.results.length === 0) { // проверяем, что список машин не пустой
          this.setState({ cars: [], has_next_page: response.data.has_next_page, cursor, isLoading: false });
        } else {
          this.setState({ cars: response.data.results, has_next_page: response.data.has_next_page, cursor, isLoading: false });
        }
      })
      .catch(error => {
        console.log(error);
        this.setState({ isLoading: false });
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
      <div>
        <ul>
          {cars.map(car => (
            <li key={car.id} class="product-wrapper">{car.brand} {car.model}, {car.body_type}, {car.fuel_type}, {car.transmission}, {car.engine} ({car.year}) Цена: {car.price}, Пробег: {car.mileage}, Битая: {car.is_bitten} <a href={car.link} rel="noreferrer" target="_blank">{car.market_type}</a></li>
              ))}
        </ul>

        <button onClick={this.handlePrevClick} disabled={cursor <= 0}>Предыдущая страница</button>
        <button onClick={this.handleNextClick} disabled={!has_next_page}>Следующая страница</button>
      </div>
    );
  }
}
      
export default CarSearchResults;