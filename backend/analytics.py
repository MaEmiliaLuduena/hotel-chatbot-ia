"""
Análisis de reservas con Pandas
Sistema de análisis de datos para optimización hotelera
"""

import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Para guardar gráficos sin mostrar ventanas
import matplotlib.pyplot as plt

def analizar_reservas():
    """Análisis completo de reservas del hotel"""
    
    print("=" * 70)
    print("📊 ANÁLISIS DE DATOS - GRAN HOTEL BELL VILLE")
    print("=" * 70)
    
    # Conectar a la base de datos
    conn = sqlite3.connect('reservas.db')
    
    # Leer datos
    df = pd.read_sql_query("SELECT * FROM reservas", conn)
    conn.close()
    
    # Convertir fechas con formato flexible
    df['fecha_checkin'] = pd.to_datetime(df['fecha_checkin'], format='mixed', errors='coerce')
    df['fecha_checkout'] = pd.to_datetime(df['fecha_checkout'], format='mixed', errors='coerce')
    df['fecha_reserva'] = pd.to_datetime(df['fecha_reserva'], format='mixed', errors='coerce')
    
    # Calcular noches
    df['noches'] = (df['fecha_checkout'] - df['fecha_checkin']).dt.days
    
    # Extraer mes y día de la semana
    df['mes'] = df['fecha_checkin'].dt.month
    df['dia_semana'] = df['fecha_checkin'].dt.day_name()
    
    print(f"\n📈 ESTADÍSTICAS GENERALES")
    print("-" * 70)
    print(f"Total de reservas:        {len(df)}")
    print(f"Ingresos totales:         ${df['precio_total'].sum():,.2f}")
    print(f"Ingreso promedio:         ${df['precio_total'].mean():,.2f}")
    print(f"Estancia promedio:        {df['noches'].mean():.1f} noches")
    print(f"Tasa de ocupación:        {calcular_ocupacion(df):.1f}%")
    
    print(f"\n🏨 ANÁLISIS POR TIPO DE HABITACIÓN")
    print("-" * 70)
    habitaciones = df.groupby('tipo_habitacion').agg({
        'id': 'count',
        'precio_total': ['sum', 'mean']
    }).round(2)
    
    habitaciones.columns = ['Reservas', 'Ingresos Totales', 'Ingreso Promedio']
    print(habitaciones.to_string())
    
    print(f"\n📅 DEMANDA POR MES")
    print("-" * 70)
    meses = df.groupby('mes').agg({
        'id': 'count',
        'precio_total': 'sum'
    }).round(2)
    
    meses.columns = ['Reservas', 'Ingresos']
    meses.index = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'][:len(meses)]
    print(meses.to_string())
    
    print(f"\n👥 ANÁLISIS POR CANTIDAD DE HUÉSPEDES")
    print("-" * 70)
    huespedes = df.groupby('huespedes').agg({
        'id': 'count',
        'precio_total': 'mean'
    }).round(2)
    
    huespedes.columns = ['Reservas', 'Precio Promedio']
    print(huespedes.to_string())
    
    print(f"\n🎯 HABITACIÓN MÁS RENTABLE")
    print("-" * 70)
    mas_rentable = df.groupby('tipo_habitacion')['precio_total'].sum().idxmax()
    ingresos_max = df.groupby('tipo_habitacion')['precio_total'].sum().max()
    print(f"Tipo: {mas_rentable}")
    print(f"Ingresos totales: ${ingresos_max:,.2f}")
    
    print(f"\n📊 RECOMENDACIONES")
    print("-" * 70)
    generar_recomendaciones(df)
    
    # Guardar análisis en archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analisis_reservas_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"ANÁLISIS DE RESERVAS - {datetime.now()}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total reservas: {len(df)}\n")
        f.write(f"Ingresos totales: ${df['precio_total'].sum():,.2f}\n")
        f.write(f"\nAnálisis por habitación:\n{habitaciones}\n")
    
    print(f"\n✅ Análisis completado con éxito")
    print("=" * 70)
    
    return df

def calcular_ocupacion(df):
    """Calcula la tasa de ocupación aproximada"""
    total_habitaciones = 29  # Total de habitaciones del hotel
    dias_periodo = 30  # Mes
    capacidad_total = total_habitaciones * dias_periodo
    
    noches_reservadas = df['noches'].sum()
    ocupacion = (noches_reservadas / capacidad_total) * 100
    
    return min(ocupacion, 100)  # Máximo 100%

def generar_recomendaciones(df):
    """Genera recomendaciones basadas en los datos"""
    
    # 1. Habitación más popular
    mas_popular = df['tipo_habitacion'].value_counts().idxmax() # Devuelve el índice (posicion) del primer valor máximo
    print(f"1. La habitación '{mas_popular}' es la más demandada")
    print(f"   💡 Considerar aumentar la cantidad de este tipo")
    
    # 2. Mes de mayor demanda
    mes_alto = df['mes'].value_counts().idxmax()
    meses_nombres = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 
                     5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto',
                     9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
    print(f"\n2. {meses_nombres[mes_alto]} es el mes de mayor demanda")
    print(f"   💡 Implementar precios dinámicos en temporada alta")
    
    # 3. Duración promedio
    promedio_noches = df['noches'].mean()
    if promedio_noches < 2:
        print(f"\n3. La estancia promedio es corta ({promedio_noches:.1f} noches)")
        print(f"   💡 Ofrecer paquetes con descuento para estadías largas")
    
    # 4. Análisis de precios
    precio_medio = df['precio_total'].mean()
    print(f"\n4. Precio promedio por reserva: ${precio_medio:,.2f}")
    print(f"   💡 Optimizar precios basados en demanda y temporada")

def generar_datos_prueba():
    """Genera datos de prueba si no existen"""
    import random
    
    conn = sqlite3.connect('reservas.db')
    cursor = conn.cursor()
    
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM reservas")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Ya existen {count} reservas en la base de datos")
        conn.close()
        return
    
    # Si la base de datos está vacía genera datos de prueba aleatorios
    print("🔄 Generando datos de prueba...")
    
    tipos_habitacion = ['matrimonial', 'doble', 'triple_matrimonial', 'triple_individual']
    nombres = ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 
               'Pedro Rodríguez', 'Laura Fernández', 'Diego Silva', 'Sofía Torres']
    
    from unidecode import unidecode
    
    # Normalizar caracteres especiales
    nombres = [unidecode(n) for n in nombres]
    
    from datetime import timedelta
    
    # Generar 50 reservas
    for i in range(50):
        nombre = random.choice(nombres)
        email = f"{nombre.split()[0].lower()}@email.com"
        telefono = f"+54 9 3537 {random.randint(100000, 999999)}"
        tipo = random.choice(tipos_habitacion)
        
        # Fechas aleatorias en los últimos 6 meses
        dias_atras = random.randint(0, 180)
        fecha_checkin = (datetime.now() - timedelta(days=dias_atras)).date()
        fecha_checkout = fecha_checkin + timedelta(days=random.randint(1, 7))
        
        huespedes = random.randint(1, 3)
        precio_total = random.randint(25000, 100000)
        estado = 'confirmada'
        fecha_reserva = datetime.now()
        
        cursor.execute('''INSERT INTO reservas 
                         (nombre, email, telefono, tipo_habitacion, fecha_checkin, 
                          fecha_checkout, huespedes, precio_total, estado, fecha_reserva)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (nombre, email, telefono, tipo, fecha_checkin, fecha_checkout,
                       huespedes, precio_total, estado, fecha_reserva))
    
    conn.commit()
    conn.close()
    
    print("✅ 50 reservas de prueba generadas")

if __name__ == "__main__":
    print("\n🏨 SISTEMA DE ANÁLISIS DE DATOS - GRAN HOTEL BELL VILLE\n")
    
    # Generar datos si no existen
    generar_datos_prueba()
    
    # Crear nombre del archivo con fecha/hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analisis_reservas_{timestamp}.txt"

    # Guardar todo lo que se imprime en consola dentro del archivo
    import sys
    original_stdout = sys.stdout  # Guardar la salida original
    with open(filename, 'w', encoding='utf-8') as f:
        sys.stdout = f  # Redirigir todo el print al archivo
        df = analizar_reservas()
        sys.stdout = original_stdout  # Restaurar la salida original
    
print(f"\n✅ Análisis completado y guardado en: {filename}\n")