from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from unidecode import unidecode
import sqlite3

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# Base de datos de habitaciones
HABITACIONES = {
    "matrimonial": {
        "nombre": "Habitación Matrimonial",
        "capacidad": 2,
        "precio_temporada_baja": 25000,
        "precio_temporada_alta": 35000,
        "descripcion": "Habitación con cama matrimonial (2 plazas), baño privado, TV, aire acondicionado y WiFi",
    },
    "doble": {
        "nombre": "Habitación Doble",
        "capacidad": 2,
        "precio_temporada_baja": 28000,
        "precio_temporada_alta": 38000,
        "descripcion": "Habitación con dos camas individuales, baño privado, TV, aire acondicionado y WiFi",
    },
    "triple_matrimonial": {
        "nombre": "Habitación Triple (1 Matrimonial + 1 Simple)",
        "capacidad": 3,
        "precio_temporada_baja": 32000,
        "precio_temporada_alta": 45000,
        "descripcion": "Habitación amplia con una cama matrimonial y una cama simple, baño privado, TV, aire acondicionado y WiFi",
    },
    "triple_individual": {
        "nombre": "Habitación Triple (3 Individuales)",
        "capacidad": 3,
        "precio_temporada_baja": 32000,
        "precio_temporada_alta": 45000,
        "descripcion": "Habitación con tres camas individuales, baño privado, TV, aire acondicionado y WiFi",
    }
}

# Información del hotel
HOTEL_INFO = """
Gran Hotel Bell Ville
Ubicación: Bell Ville, Córdoba, Argentina
Dirección: Av. San Martín 123, Bell Ville

SERVICIOS:
- WiFi gratuito en todas las áreas
- Desayuno buffet incluido (7:00 - 10:00 hs)
- Estacionamiento gratuito
- Servicio de limpieza diario
- Recepción 24 horas
- Piscina climatizada
- Gimnasio
- Sala de conferencias

HORARIOS:
- Check-in: 14:00 hs
- Check-out: 10:00 hs

POLÍTICAS:
- Cancelación gratuita hasta 48 hs antes del check-in
- Se requiere tarjeta de crédito para garantizar la reserva
- No se permiten mascotas
- Niños menores de 5 años no pagan

TEMPORADAS:
- Temporada Alta: Diciembre a Febrero, Semana Santa, feriados largos
- Temporada Baja: Resto del año

FORMAS DE PAGO:
- Efectivo
- Tarjetas de débito y crédito (Visa, Mastercard, American Express)
- Transferencia bancaria
"""

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('reservas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reservas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT,
                  email TEXT,
                  telefono TEXT,
                  tipo_habitacion TEXT,
                  fecha_checkin TEXT,
                  fecha_checkout TEXT,
                  huespedes INTEGER,
                  precio_total REAL,
                  estado TEXT,
                  fecha_reserva TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Contexto del sistema para Gemini
SYSTEM_PROMPT = f"""Eres un asistente virtual del Gran Hotel Bell Ville en Bell Ville, Córdoba, Argentina. 
Tu nombre es BellBot y eres amable, profesional y eficiente.

INFORMACIÓN DEL HOTEL:
{HOTEL_INFO}

TIPOS DE HABITACIONES DISPONIBLES:
{json.dumps(HABITACIONES, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
1. Saluda cordialmente y ofrece ayuda
2. Si preguntan por habitaciones, describe las opciones disponibles con sus características y precios
3. Para hacer una reserva, solicita: nombre, email, teléfono, tipo de habitación, fechas (check-in y check-out), número de huéspedes
4. Calcula precios según la temporada (verifica las fechas)
5. Responde preguntas sobre servicios, políticas, ubicación, etc.
6. Si no tienes información, sé honesto y ofrece contactar a recepción
7. Mantén un tono profesional pero amigable
8. Responde siempre en español argentino

IMPORTANTE SOBRE IMÁGENES:
- NO menciones que vas a mostrar imágenes, fotos o contenido visual
- NO digas frases como "te muestro la imagen" o "aquí está la foto"
- El sistema automáticamente muestra las imágenes cuando preguntan por habitaciones
- Simplemente describe las características de las habitaciones sin mencionar imágenes
- Enfócate en dar información útil: tamaño, comodidades, precio, capacidad

EJEMPLO CORRECTO:
Usuario: "Quiero ver una habitación matrimonial"
Tu respuesta: "¡Por supuesto! La Habitación Matrimonial es ideal para parejas. Cuenta con una cama de 2 plazas (1.40m x 1.90m), baño privado, aire acondicionado, TV LED, WiFi gratuito y minibar. El precio es de $25,000 por noche en temporada baja y $35,000 en temporada alta. ¿Te gustaría hacer una reserva o necesitas información sobre otro tipo de habitación?"

EJEMPLO INCORRECTO (NO HACER):
"Te muestro la imagen de la habitación matrimonial..." ← NO DECIR ESTO
"Si estuviéramos en una plataforma visual..." ← NO DECIR ESTO
"Aquí tienes la foto..." ← NO DECIR ESTO
"""

def es_temporada_alta(fecha_str):
    """Determina si una fecha está en temporada alta"""
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        mes = fecha.month
        
        # Temporada alta: Diciembre-Febrero (12, 1, 2)
        if mes in [12, 1, 2]:
            return True
        
        # Semana Santa (aproximación: marzo-abril)
        if mes in [3, 4]:
            dia = fecha.day
            if 10 <= dia <= 20:  # Aproximación de Semana Santa
                return True
        
        return False
    except:
        return False

def calcular_precio_reserva(tipo_habitacion, fecha_checkin, fecha_checkout):
    """Calcula el precio total de una reserva"""
    try:
        checkin = datetime.strptime(fecha_checkin, "%Y-%m-%d")
        checkout = datetime.strptime(fecha_checkout, "%Y-%m-%d")
        noches = (checkout - checkin).days
        
        if noches <= 0:
            return None
        
        habitacion = HABITACIONES.get(tipo_habitacion)
        if not habitacion:
            return None
        
        precio_total = 0
        fecha_actual = checkin
        
        while fecha_actual < checkout:
            if es_temporada_alta(fecha_actual.strftime("%Y-%m-%d")):
                precio_total += habitacion["precio_temporada_alta"]
            else:
                precio_total += habitacion["precio_temporada_baja"]
            fecha_actual += timedelta(days=1)
        
        return {
            "noches": noches,
            "precio_total": precio_total,
            "precio_promedio_noche": precio_total / noches
        }
    except:
        return None

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        # Construir el contexto de la conversación
        chat_context = SYSTEM_PROMPT + "\n\nCONVERSACIÓN:\n"
        for msg in conversation_history[-10:]:  # Últimos 10 mensajes
            role = "Usuario" if msg['role'] == 'user' else "BellBot"
            chat_context += f"{role}: {msg['content']}\n"
        
        chat_context += f"Usuario: {user_message}\nBellBot:"
        
        # Generar respuesta con Gemini
        response = model.generate_content(chat_context)
        bot_response = response.text
        
        # Detectar si se mencionan habitaciones para enviar imágenes
        mostrar_imagenes = []
        mensaje_lower = user_message.lower()
        
        if any(word in mensaje_lower for word in ['habitacion', 'habitación', 'cuarto', 'tipo', 'opciones', 'mostrar', 'ver', 'fotos']):
            if 'matrimonial' in mensaje_lower and 'triple' not in mensaje_lower:
                mostrar_imagenes.append('matrimonial')
            if 'doble' in mensaje_lower:
                mostrar_imagenes.append('doble')
            if 'triple' in mensaje_lower:
                if 'matrimonial' in mensaje_lower or 'simple' in mensaje_lower:
                    mostrar_imagenes.append('triple_matrimonial')
                if 'individual' in mensaje_lower or 'tres camas' in mensaje_lower:
                    mostrar_imagenes.append('triple_individual')
            
            # Si no se especifica tipo, mostrar todas
            if not mostrar_imagenes and any(word in mensaje_lower for word in ['todas', 'tipos', 'opciones', 'disponibles']):
                mostrar_imagenes = list(HABITACIONES.keys())
        
        return jsonify({
            'response': bot_response,
            'imagenes': mostrar_imagenes,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/habitaciones', methods=['GET'])
def get_habitaciones():
    return jsonify(HABITACIONES)

@app.route('/api/habitacion/<tipo>', methods=['GET'])
def get_habitacion(tipo):
    habitacion = HABITACIONES.get(tipo)
    if habitacion:
        return jsonify(habitacion)
    return jsonify({'error': 'Habitación no encontrada'}), 404

@app.route('/api/calcular-precio', methods=['POST'])
def calcular_precio():
    try:
        data = request.json
        tipo = data.get('tipo_habitacion')
        checkin = data.get('fecha_checkin')
        checkout = data.get('fecha_checkout')
        
        resultado = calcular_precio_reserva(tipo, checkin, checkout)
        
        if resultado:
            return jsonify(resultado)
        return jsonify({'error': 'Error al calcular precio'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservar', methods=['POST'])
def crear_reserva():
    try:
        data = request.json
        
        # Validar datos requeridos
        required_fields = ['nombre', 'email', 'telefono', 'tipo_habitacion', 
                          'fecha_checkin', 'fecha_checkout', 'huespedes']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # NORMALIZAR DATOS (eliminar tildes y ñ)
        nombre_normalizado = unidecode(data['nombre'])
        email_normalizado = unidecode(data['email']).lower()
        telefono_limpio = data['telefono'].strip()
        
        # Calcular precio
        precio_info = calcular_precio_reserva(
            data['tipo_habitacion'],
            data['fecha_checkin'],
            data['fecha_checkout']
        )
        
        if not precio_info:
            return jsonify({'error': 'Error al calcular precio'}), 400
        
        # Guardar reserva CON DATOS NORMALIZADOS
        conn = sqlite3.connect('reservas.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO reservas 
                     (nombre, email, telefono, tipo_habitacion, fecha_checkin, 
                      fecha_checkout, huespedes, precio_total, estado, fecha_reserva)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (nombre_normalizado,          # <- NORMALIZADO
                   email_normalizado,            # <- NORMALIZADO
                   telefono_limpio,              # <- LIMPIO
                   data['tipo_habitacion'], 
                   data['fecha_checkin'], 
                   data['fecha_checkout'], 
                   data['huespedes'], 
                   precio_info['precio_total'], 
                   'confirmada', 
                   datetime.now().isoformat()))
        
        reserva_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'reserva_id': reserva_id,
            'precio_total': precio_info['precio_total'],
            'noches': precio_info['noches'],
            'mensaje': f'Reserva confirmada! ID: {reserva_id}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservas', methods=['GET'])
def get_reservas():
    try:
        conn = sqlite3.connect('reservas.db')
        c = conn.cursor()
        c.execute('SELECT * FROM reservas ORDER BY fecha_reserva DESC LIMIT 50')
        reservas = c.fetchall()
        conn.close()
        
        reservas_list = []
        for r in reservas:
            reservas_list.append({
                'id': r[0],
                'nombre': r[1],
                'email': r[2],
                'telefono': r[3],
                'tipo_habitacion': r[4],
                'fecha_checkin': r[5],
                'fecha_checkout': r[6],
                'huespedes': r[7],
                'precio_total': r[8],
                'estado': r[9],
                'fecha_reserva': r[10]
            })
        
        return jsonify(reservas_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API funcionando correctamente'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)