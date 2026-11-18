export interface Car {
  id: number;
  brand: string;
  model: string;
  category: string;
  city: string;
  seats: number;
  image_url: string;
  daily_rate_uah: string;
  deposit_uah: string;
}
export async function listCars(city = ''): Promise<Car[]> {
  const query = city.trim() ? `?city=${encodeURIComponent(city.trim())}` : '';
  const response = await fetch(`/api/cars/${query}`);
  if (!response.ok) throw new Error(`Сервер повернув ${response.status}`);
  const json: unknown = await response.json();
  if (!Array.isArray(json)) throw new Error('Неочікувана відповідь API');
  return json as Car[];
}
