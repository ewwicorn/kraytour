/// <reference types="vite/client" />

declare global {
  interface Window {
    ymaps3: any;
  }
}

interface ImportMetaEnv {
  readonly VITE_YANDEX_MAPS_API_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

export {};