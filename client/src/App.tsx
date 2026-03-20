import YandexMap from './components/YandexMap';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🗺️ Карта для Kraytour</h1>
      <p>Yandex Maps API v3</p>
      <YandexMap
        center={[38.975313 , 45.035470]} // Краснодар
        zoom={12}
        height="700px"
        width='900px'
      />
    </div>
  );
}

export default App;