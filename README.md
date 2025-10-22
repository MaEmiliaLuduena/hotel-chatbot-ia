# 🏨 Chatbot IA para Gran Hotel Bell Ville
# Sistema de Gestión de Reservas con Inteligencia Artificial

## 📖 Descripción
Sistema inteligente de chatbot para la gestión automatizada de reservas hoteleras. Utiliza procesamiento de lenguaje natural (NLP) con Gemini AI para proporcionar una experiencia conversacional natural, con soporte para texto y voz.

## 🎯 Características Principales
* ✅ __Conversación Natural:__ Chat inteligente con comprensión contextual
* 🎤 __Reconocimiento de Voz:__ Speech-to-Text integrado
* 🔊 __Síntesis de Voz:__ Respuestas en audio
* 🖼️ __Envío Automático de Imágenes:__ Muestra habitaciones según consultas
* 📅 __Sistema de Reservas:__ Gestión completa de reservas
* 💰 __Cálculo Automático de Precios:__ Por temporada alta/baja
* 📊 __Base de Datos:__ Persistencia de reservas con SQLite
* 🎨 __Interfaz Moderna:__ Diseño responsivo con React y Tailwind

---

## 🚀 Tecnologías Utilizadas
### Backend
* __Python__
* __Flask__ - Framework web
* __Flask-CORS__ - Manejo de CORS
* __Google Generative AI (Gemini)__ - Procesamiento de lenguaje natural
* __SQLite__ - Base de datos
* __Pandas__ - Análisis de datos
* __Scikit-learn__ - Machine Learning

### Frontend
* __React__ - Biblioteca UI
* __Vite__ - Build tool
* __Tailwind CSS__ - Framework CSS
* __Lucide React__ - Iconos
* __Web Speech API__ - Reconocimiento y síntesis de voz

---

## 📦 Instalación
### 🔧 Requisitos Previos

Antes de comenzar, debes tener instalado:

1. **Python 3.8 o superior**
   - Descarga: https://www.python.org/downloads/
   - Verifica con: `python --version` o `python3 --version`

2. **Node.js 16 o superior** (para React)
   - Descarga: https://nodejs.org/
   - Verifica con: `node --version`

---

### Paso 1: Clonar el Repositorio
```bash
gitclone https://github.com/MaEmiliaLuduena/hotel-chatbot-ia
cd hotel-chatbot-ia
```

O crear la estructura manualmente:

```bash
# Crear carpeta principal
mkdir hotel-chatbot-ia
cd hotel-chatbot-ia

# Crear subcarpetas
mkdir backend frontend datos
```

---

### 🐍 Paso 2: Configurar Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

__Crear archivo .env:__
```env
GEMINI_aquiGEMINI_API_KEY=tu_api_key_aqui
FLASK_developmentFLASK_ENV=development
FLASK_TrueFLASK_DEBUG=True
```

__Obtener API Key de Gemini:__
1. Ve a https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta Google
3. Crea una nueva API Key
4. Cópiala en el archivo .env

---

### 🎨 Paso 3: Configurar Frontend (React)
```bash
cd ../frontend

# Instalar dependencias
npm install

# Si no existe el proyecto, crearlo primero:
npm create vite@latest . -- --template react
npm install
npm install lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

__Configurar Tailwind CSS en tailwind.config.js:__
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

__Actualizar src/index.css:__
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

__Editar main.jsx__

Edita `src/main.jsx`:

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

### 📂 Paso 4: Estructura Final del Proyecto

```
hotel-chatbot-ia/
├── backend/
│   ├── analytics.py ← Análisis de reservas con Pandas
│   ├── app.py ← API principal (Flask) - TIEMPO REAL
│   ├── .env ← Credenciales API Key Gemini
│   ├── requirements.txt ← Dependencias
│   ├── reservas.db (se crea automáticamente)
│   ├── test_precision.py ← Testing del chatbot
│   └── venv/ (entorno virtual)
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── node_modules/
├── datos/
|    └── hotel_info.json
└── README.md
```

---

## 🚀 Ejecución del proyecto
### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate # o venv\Scripts\activate en Windows
python app.py

# Deberías ver:
# * Running on http://127.0.0.1:5000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev

# Deberías ver:
# VITE v5.0.0  ready in XXX ms
# ➜  Local:   http://localhost:5173/
```

### Terminal 3: Backend - Análisis de datos
```bash
cd backend
python analytics.py
```
Esto generará un archivo.txt con análisis de datos y recomendaciones de acuerdo a la demanda de habitaciones del hotel

### Terminal 4: Backend
### 🧪 Validación de Precisión

El chatbot ha sido probado con un dataset de 31 preguntas categorizadas.

### Ejecutar pruebas:
```bash
cd backend
python test_precision.py
```

#### Resultados:

- **Precisión alcanzada:** 93.75%
- **Objetivo requerido:** ≥ 90% ✅
- **Preguntas evaluadas:** 31
- **Respuestas correctas:** 29

Los resultados detallados se guardan automáticamente en formato JSON para auditoría.

---

## 📝 Licencia
Este proyecto fue desarrollado como proyecto final para el curso de Big Data & Inteligencia Artificial.

__Autor:__ María Emilia Ludueña

__Fecha:__ 21 Octubre 2025

__Institución:__ Ayi Academy - Ayi Group

