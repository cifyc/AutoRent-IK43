import type { Car } from '../api';

export function CarCard({car}: {car: Car}) {
  return <article className="car-card">
    <div className="car-card__category">{car.category} · {car.city}</div>
    <h2>{car.brand} {car.model}</h2>
    <p>Місць: {car.seats}</p>
    <div className="car-card__price">{Number(car.daily_rate_uah).toLocaleString('uk-UA', {minimumFractionDigits:2})} грн / доба</div>
    <p>Застава: {Number(car.deposit_uah).toLocaleString('uk-UA', {minimumFractionDigits:2})} грн</p>
  </article>;
}
