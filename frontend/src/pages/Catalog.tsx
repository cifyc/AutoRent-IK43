import { useEffect, useState } from 'react';
import { listCars, type Car } from '../api';
import { CarCard } from '../components/CarCard';

export function Catalog() {
  const [city, setCity] = useState('');
  const [cars, setCars] = useState<Car[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    setLoading(true);
    listCars(city).then(data => {if (active) {setCars(data); setError('');}})
      .catch(e => {if (active) setError(e instanceof Error ? e.message : 'Помилка мережі');})
      .finally(() => {if (active) setLoading(false);});
    return () => { active = false; };
  }, [city]);
  return <main className="layout">
    <header><span className="eyebrow">НАВЧАЛЬНИЙ ПРОЄКТ</span><h1>AutoRent</h1><p>Каталог автомобілів для оренди. Бронювання виконується сервером через захищений API.</p></header>
    <section className="filter"><label htmlFor="city">Місто отримання</label><input id="city" placeholder="Наприклад, Київ" value={city} onChange={event => setCity(event.target.value)}/></section>
    {loading ? <p>Завантаження автомобілів…</p> : error ? <p role="alert">Не вдалося завантажити каталог: {error}</p> : cars.length ? <div className="cards">{cars.map(car => <CarCard key={car.id} car={car}/>)}</div> : <p>Доступних автомобілів за цим фільтром немає.</p>}
    <footer>Прототип для лабораторної роботи №4. Авторизація та вебформа бронювання — подальший етап інтерфейсу.</footer>
  </main>;
}
