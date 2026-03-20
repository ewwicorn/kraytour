import { useEffect, useRef, useState } from 'react';

interface YandexMapProps {
  center?: [number, number];
  zoom?: number;
  height?: string;
  width?: string;
}

const YandexMap: React.FC<YandexMapProps> = ({
  center = [37.6173, 55.7558], // Москва по умолчанию [lng, lat]
  zoom = 12,
  height = '700px',
  width = '100%',
}) => {
  const containerRef = useRef<HTMLDivElement>(null); // ссылка на DOM-элемент карты
  const [loading, setLoading] = useState(true);      // состояние загрузки
  const [error, setError] = useState<string | null>(null); // состояние ошибки

  useEffect(() => {
    // Читаем ключ Яндекс Карт из .env
    const key = import.meta.env.VITE_YANDEX_MAPS_API_KEY;

    if (!key) {
      setError('Ключ VITE_YANDEX_MAPS_API_KEY не найден в .env');
      setLoading(false);
      return;
    }

    // ─── Утилита: загрузка внешнего скрипта ───────────────────────────────────
    // Создаёт <script> тег и возвращает Promise, который резолвится когда скрипт загружен.
    // Если скрипт с таким src уже есть в DOM — просто резолвится сразу.
    function loadScript(src: string): Promise<void> {
      return new Promise((resolve, reject) => {
        if (document.querySelector(`script[src="${src}"]`)) {
          resolve();
          return;
        }
        const s = document.createElement('script');
        s.src = src;
        s.async = true;
        s.onload = () => resolve();
        s.onerror = () => reject(new Error(`Не удалось загрузить: ${src}`));
        document.head.appendChild(s);
      });
    }

    // ─── Основная функция инициализации карты ─────────────────────────────────
    async function initMap() {
      try {

        // 1. Загружаем основной скрипт Яндекс Карт v3
        await loadScript(
          `https://api-maps.yandex.ru/v3/?apikey=${key}&lang=ru_RU`
        );

        if (!window.ymaps3) throw new Error('ymaps3 не найден после загрузки');

        // 2. Ждём пока все внутренние модули ymaps3 будут готовы
        await window.ymaps3.ready;

        const ymaps3 = window.ymaps3;

        // 3. Регистрируем CDN откуда ymaps3 будет подгружать дополнительные пакеты.
        //    Без этого ymaps3.import('@yandex/ymaps3-default-ui-theme') не знает откуда брать файл.
        ymaps3.import.registerCdn(
          'https://cdn.jsdelivr.net/npm/{package}',
          '@yandex/ymaps3-default-ui-theme@latest'
        );

        // 4. Деструктурируем нужные классы из основного пакета ymaps3
        const {
          YMap,                       // Основной класс карты
          YMapDefaultSchemeLayer,     // Слой со схемой дорог/улиц
          YMapDefaultFeaturesLayer,   // Слой для отображения маркеров и линий
          YMapControls,               // Контейнер для кнопок управления
          YMapFeature,                // Класс для рисования линий/полигонов
        } = ymaps3;

        // 5. Подгружаем UI-пакет с готовыми компонентами (зум, маршруты, маркеры)
        //    Этот пакет не входит в основной — он загружается отдельно с CDN
        const {
          YMapZoomControl,    // Кнопки + и - для зума
          YMapRouteControl,   // Панель "Откуда → Куда" с вводом адресов
          YMapDefaultMarker,  // Красивый маркер с иконкой
        } = await ymaps3.import('@yandex/ymaps3-default-ui-theme');

        if (!containerRef.current) return;

        // 6. Создаём карту и прикрепляем к DOM-элементу
        const map = new YMap(containerRef.current, {
          location: { center, zoom },
        });

        // 7. Добавляем базовые слои на карту
        map.addChild(new YMapDefaultSchemeLayer({}));   // слой карты (улицы, дома)
        map.addChild(new YMapDefaultFeaturesLayer({})); // слой для наших объектов

        // 8. Добавляем кнопки зума справа
        map.addChild(
          new YMapControls({ position: 'right' }).addChild(
            new YMapZoomControl({})
          )
        );

        // ─── Маркеры точек А и Б ──────────────────────────────────────────────
        // Создаём заранее, но НЕ добавляем на карту — они появятся когда
        // пользователь введёт адреса в панели маршрутизации

        let routeFeatures: any[] = []; // массив для хранения линий маршрута на карте

        // Маркер точки А (зелёный — старт)
        const fromMarker = new YMapDefaultMarker({
          coordinates: center,
          color: 'green',
          draggable: true, // можно перетаскивать мышью
          onDragEnd: (coords: [number, number]) => {
            // При перетаскивании обновляем точку А в панели маршрута
            routeControl.update({ waypoints: [coords, null] });
          },
        });

        // Маркер точки Б (красный — финиш)
        const toMarker = new YMapDefaultMarker({
          coordinates: center,
          color: 'red',
          draggable: true,
          onDragEnd: (coords: [number, number]) => {
            // При перетаскивании обновляем точку Б в панели маршрута
            routeControl.update({ waypoints: [null, coords] });
          },
        });

        // ─── Панель маршрутизации ──────────────────────────────────────────────
        const routeControl = new YMapRouteControl({
          waypoints: [null, null],                          // изначально точки пустые
          waypointsPlaceholders: ['Откуда', 'Куда'],        // плейсхолдеры в инпутах

          // ── РОУТЕР: используем OSRM (бесплатный, без ключа) ────────────────
          // Яндекс Router API платный, поэтому переопределяем встроенный роутер
          // на бесплатный OSRM (Open Source Routing Machine).
          // ymaps3 вызывает эту функцию когда нужно построить маршрут,
          // и ожидает массив объектов с методами toRoute() и toSteps().
          route: async (args: any) => {
            const points = args.params.points; // [[lng, lat], [lng, lat]]
            const type = args.params.type ?? 'driving';

            const [from, to] = points;

            const modeMap: Record<string, string> = {
                driving: 'driving',
                walking: 'foot',
                transit: 'driving',
                truck: 'driving',
            };
            const mode = modeMap[type] ?? 'driving';

            const url =
                `https://router.project-osrm.org/route/v1/${mode}/` +
                `${from[0]},${from[1]};${to[0]},${to[1]}` +
                `?overview=full&geometries=geojson&steps=true`;

            const res = await fetch(url);
            if (!res.ok) throw new Error(`OSRM ошибка: ${res.status}`);

            const data = await res.json();
            const route = data.routes?.[0];

            if (!route) throw new Error('OSRM не вернул маршрут');

            const geometry = route.geometry; // GeoJSON LineString

            // Собираем шаги из всех legs
            const steps = route.legs
                .flatMap((leg: any) => leg.steps)
                .map((step: any) => ({
                geometry: step.geometry,
                properties: { mode: type },
                }));

            // ymaps3 ожидает массив объектов с методами toRoute() и toSteps()
            return [
                {
                toRoute: () => ({
                    geometry,
                    properties: { mode: type },
                }),
                toSteps: () => steps.length > 0 ? steps : [{ geometry, properties: { mode: type } }],
                },
            ];
            },

          // ── Колбек: маршрут успешно построен ───────────────────────────────
          // Вызывается когда роутер вернул результат.
          // Здесь мы рисуем линию маршрута на карте.
          onRouteResult(result: any, type: string) {
            // Удаляем старый маршрут если был
            routeFeatures.forEach(f => map.removeChild(f));
            routeFeatures = [];

            try {
              if (type !== 'transit') {
                // Для авто/пешком — рисуем одну линию
                const { geometry } = result.toRoute();
                const feature = new YMapFeature({
                  geometry,
                  style: {
                    stroke: [{ color: '#3b82f6', width: 5 }], // синяя линия
                    simplificationRate: 0, // не упрощать геометрию
                  },
                });
                map.addChild(feature);
                routeFeatures.push(feature);
              } else {
                // Для общественного транспорта — рисуем каждый шаг отдельно
                result.toSteps().forEach((step: any) => {
                  const feature = new YMapFeature({
                    geometry: step.geometry,
                    style: {
                      stroke: [{ color: '#8b5cf6', width: 4 }], // фиолетовая линия
                      simplificationRate: 0,
                    },
                  });
                  map.addChild(feature);
                  routeFeatures.push(feature);
                });
              }
            } catch (e) {
              console.error('Ошибка отрисовки маршрута:', e);
            }
          },

          // ── Колбек: пользователь изменил точки маршрута ─────────────────────
          // Вызывается при вводе адреса или перетаскивании маркера.
          // Здесь синхронизируем маркеры на карте с точками в панели.
          onUpdateWaypoints(waypoints: any[]) {
            const [from, to] = waypoints;

            // Обновляем маркер точки А
            if (from?.geometry?.coordinates) {
              fromMarker.update({ coordinates: from.geometry.coordinates });
              // Добавляем на карту если ещё не добавлен
              if (!map.children.includes(fromMarker)) map.addChild(fromMarker);
            } else {
              // Убираем с карты если точка сброшена
              if (map.children.includes(fromMarker)) map.removeChild(fromMarker);
            }

            // Обновляем маркер точки Б
            if (to?.geometry?.coordinates) {
              toMarker.update({ coordinates: to.geometry.coordinates });
              if (!map.children.includes(toMarker)) map.addChild(toMarker);
            } else {
              if (map.children.includes(toMarker)) map.removeChild(toMarker);
            }

            // Если одна из точек убрана — стираем линию маршрута
            if (!from || !to) {
              routeFeatures.forEach(f => map.removeChild(f));
              routeFeatures = [];
            }
          },

          // ── Колбек: ошибка построения маршрута ──────────────────────────────
          // Вызывается если роутер не смог построить маршрут
          onBuildRouteError() {
            console.error('Не удалось построить маршрут');
            routeFeatures.forEach(f => map.removeChild(f));
            routeFeatures = [];
          },
        });

        // 9. Добавляем панель маршрутизации в левый верхний угол
        map.addChild(
          new YMapControls({ position: 'top left' }).addChild(routeControl)
        );

        setLoading(false);
        console.log('✅ Карта загружена');

      } catch (err: any) {
        console.error(err);
        setError(err.message ?? 'Ошибка при инициализации карты');
        setLoading(false);
      }
    }

    initMap();
  }, [center, zoom]);

  // ─── Рендер ошибки ──────────────────────────────────────────────────────────
  if (error) {
    return (
      <div style={{ color: 'red', padding: '20px', fontSize: '16px' }}>
        ❌ Ошибка: {error}
      </div>
    );
  }

  // ─── Рендер карты ───────────────────────────────────────────────────────────
  return (
    <div style={{ position: 'relative', width, height }}>

      {/* Заглушка пока карта грузится */}
      {loading && (
        <div style={{
          position: 'absolute',
          inset: 0,
          background: '#f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '18px',
          zIndex: 1,
        }}>
          Загрузка карты...
        </div>
      )}

      {/* Контейнер куда ymaps3 рендерит карту */}
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

    </div>
  );
};

export default YandexMap;