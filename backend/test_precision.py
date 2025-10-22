"""
Script para validar la precisión del chatbot (objetivo: 90%+)
Este script prueba el chatbot con un conjunto de preguntas predefinidas
y verifica si las respuestas contienen la información esperada.
"""

import requests
import json
import time
from datetime import datetime

# URL del API
API_URL = "http://localhost:5000/api/chat"

# Dataset de pruebas - Lista de tuplas: (pregunta, palabras_clave_esperadas)
DATASET_PRUEBAS = [
    # Información básica del hotel
    ("¿Cuál es la dirección del hotel?", ["San Martín", "123", "Bell Ville"]),
    ("¿Dónde está ubicado el hotel?", ["Bell Ville", "Córdoba", "Argentina"]),
    ("¿Tienen WiFi?", ["WiFi", "gratuito", "gratis"]),
    ("¿El WiFi es gratis?", ["gratuito", "gratis", "incluido"]),
    
    # Horarios
    ("¿A qué hora es el check-in?", ["14:00", "14", "dos de la tarde"]),
    ("¿A qué hora es el check-out?", ["10:00", "10", "diez de la mañana"]),
    ("¿Qué horario tiene el desayuno?", ["7:00", "10:00", "buffet"]),
    
    # Habitaciones
    ("¿Qué tipos de habitaciones tienen?", ["matrimonial", "doble", "triple"]),
    ("¿Tienen habitación matrimonial?", ["matrimonial", "cama matrimonial", "2 plazas"]),
    ("¿Tienen habitación doble?", ["doble", "dos camas", "individuales"]),
    ("¿Tienen habitación triple?", ["triple", "tres", "3"]),
    ("¿Cuántas personas caben en una habitación matrimonial?", ["2", "dos"]),
    
    # Precios
    ("¿Cuánto cuesta una habitación matrimonial?", ["25000", "35000", "precio", "temporada"]),
    ("¿Cuánto cuesta la habitación más barata?", ["matrimonial", "25000", "precio"]),
    ("¿Cuál es la diferencia entre temporada alta y baja?", ["temporada", "alta", "baja", "precio"]),
    
    # Servicios
    ("¿Tienen estacionamiento?", ["estacionamiento", "gratuito", "gratis"]),
    ("¿Tienen piscina?", ["piscina", "climatizada"]),
    ("¿Tienen gimnasio?", ["gimnasio"]),
    ("¿Sirven desayuno?", ["desayuno", "buffet", "incluido"]),
    ("¿Tienen recepción 24 horas?", ["24 horas", "recepción"]),
    
    # Políticas
    ("¿Cuál es la política de cancelación?", ["cancelación", "48", "horas"]),
    ("¿Permiten mascotas?", ["mascotas", "no"]),
    ("¿Los niños pagan?", ["niños", "5 años", "no pagan"]),
    ("¿Necesito tarjeta de crédito?", ["tarjeta", "crédito", "garantizar"]),
    
    # Formas de pago
    ("¿Qué formas de pago aceptan?", ["efectivo", "tarjeta", "crédito"]),
    ("¿Puedo pagar con tarjeta?", ["tarjeta", "débito", "crédito", "Visa", "Mastercard"]),
    
    # Consultas de reserva
    ("¿Cómo hago una reserva?", ["reserva", "nombre", "email", "fechas"]),
    ("¿Qué información necesito para reservar?", ["nombre", "email", "teléfono", "fechas"]),
    
    # Consultas generales
    ("¿Tienen sala de conferencias?", ["sala", "conferencias"]),
    ("¿El hotel tiene aire acondicionado?", ["aire acondicionado", "todas"]),
    ("¿Las habitaciones tienen baño privado?", ["baño", "privado", "todas"]),
]

def verificar_respuesta(respuesta, palabras_clave):
    """
    Verifica si la respuesta contiene al menos una de las palabras clave esperadas
    """
    respuesta_lower = respuesta.lower()
    
    # Normalizar caracteres especiales
    respuesta_lower = respuesta_lower.replace('á', 'a').replace('é', 'e').replace('í', 'i')
    respuesta_lower = respuesta_lower.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    
    coincidencias = 0
    for palabra in palabras_clave:
        palabra_lower = palabra.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i')
        palabra_lower = palabra_lower.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        
        if palabra_lower in respuesta_lower:
            coincidencias += 1
    
    # Considera correcto si al menos 1 palabra clave está presente
    return coincidencias > 0

def ejecutar_pruebas():
    """
    Ejecuta todas las pruebas y calcula la precisión
    """
    print("=" * 80)
    print("INICIANDO PRUEBAS DE PRECISIÓN DEL CHATBOT")
    print("=" * 80)
    print(f"\nTotal de preguntas en el dataset: {len(DATASET_PRUEBAS)}\n")
    print("-" * 80)
    
    resultados = []
    correctas = 0
    
    # Por cada pregunta evía una petición POST a la API
    for i, (pregunta, palabras_clave) in enumerate(DATASET_PRUEBAS, 1):
        print(f"\n[{i}/{len(DATASET_PRUEBAS)}] Pregunta: {pregunta}")
        print(f"Palabras clave esperadas: {', '.join(palabras_clave)}")
        
        try:
            # Hacer request al API
            response = requests.post(
                API_URL,
                json={
                    'message': pregunta, # la pregunta que haría el usuario
                    'history': [] # vacío (no hay contexto previo)
                },
                timeout=30 # 30 segundos máximo para recibir respuesta
            )
            
            # Si la respuesta es correcta obtiene el texto del chatbot
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get('response', '')
                
                # Verificar si la respuesta es correcta
                es_correcta = verificar_respuesta(respuesta, palabras_clave)
                
                if es_correcta:
                    correctas += 1
                    status = "✅ CORRECTO"
                else:
                    status = "❌ INCORRECTO"
                
                print(f"Respuesta: {respuesta[:150]}...")
                print(f"Estado: {status}")
                
                resultados.append({
                    'pregunta': pregunta,
                    'respuesta': respuesta,
                    'palabras_clave': palabras_clave,
                    'correcta': es_correcta
                })
            # Si hay error HTTP o de conexión, lo registra como incorrecto
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                resultados.append({
                    'pregunta': pregunta,
                    'respuesta': f"Error: {response.status_code}",
                    'palabras_clave': palabras_clave,
                    'correcta': False
                })
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            resultados.append({
                'pregunta': pregunta,
                'respuesta': f"Error: {str(e)}",
                'palabras_clave': palabras_clave,
                'correcta': False
            })
        
        # Espera 0.5 segundos antes de la siguiente prueba
        time.sleep(0.5)
        print("-" * 80)
    
    # Calcular precisión
    precision = (correctas / len(DATASET_PRUEBAS)) * 100
    
    # Mostrar resultados finales
    print("\n" + "=" * 80)
    print("RESULTADOS FINALES")
    print("=" * 80)
    print(f"\nTotal de preguntas: {len(DATASET_PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Respuestas incorrectas: {len(DATASET_PRUEBAS) - correctas}")
    print(f"\n🎯 PRECISIÓN ALCANZADA: {precision:.2f}%")
    
    if precision >= 90:
        print("\n✅ ¡OBJETIVO CUMPLIDO! Precisión >= 90%")
    else:
        print(f"\n⚠️  Precisión por debajo del objetivo. Faltan {90 - precision:.2f}% para llegar al 90%")
    
    # Guardar resultados en archivo JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resultados_precision_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_preguntas': len(DATASET_PRUEBAS),
            'correctas': correctas,
            'precision': precision,
            'resultados': resultados
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Resultados guardados en: {filename}")
    print("=" * 80)
    
    return precision, resultados

if __name__ == "__main__":
    try:
        # Antes de correr las pruebas verifica que el servidor esté corriendo
        try:
            health_check = requests.get("http://localhost:5000/api/health", timeout=5)
            if health_check.status_code != 200:
                print("⚠️  ADVERTENCIA: El servidor no responde correctamente")
                print("Asegúrate de que el backend esté corriendo en http://localhost:5000")
                exit(1)
        except:
            print("❌ ERROR: No se puede conectar al servidor")
            print("Asegúrate de que el backend esté corriendo en http://localhost:5000")
            exit(1)
        
        # Ejecutar pruebas
        precision, resultados = ejecutar_pruebas()
        
        # Mostrar preguntas que fallaron
        if precision < 100:
            print("\n" + "=" * 80)
            print("PREGUNTAS QUE FALLARON:")
            print("=" * 80)
            for r in resultados:
                if not r['correcta']:
                    print(f"\n❌ Pregunta: {r['pregunta']}")
                    print(f"   Esperaba: {', '.join(r['palabras_clave'])}")
                    print(f"   Obtuvo: {r['respuesta'][:100]}...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {str(e)}")