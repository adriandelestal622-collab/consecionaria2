from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# --- Configuración Inicial ---
app = Flask(__name__) 

# --- Conexión a MySQL (XAMPP) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/concesionaria'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creamos el objeto para la base de datos
db = SQLAlchemy(app)

# ============================================
# MODELOS DE BASE DE DATOS
# ============================================

# --- Modelo de la tabla "consulta" ---
class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)

# --- Modelo de la tabla "turno" ---
class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    auto_interes = db.Column(db.String(100))
    mensaje = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.String(20), default='pendiente')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'email': self.email,
            'fecha': self.fecha,
            'hora': self.hora,
            'auto_interes': self.auto_interes,
            'mensaje': self.mensaje,
            'fecha_creacion': self.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'estado': self.estado
        }

# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def home():
    return render_template('index.html')

# ============================================
# RUTA: GUARDAR CONSULTA
# ============================================

@app.route('/guardar-consulta', methods=['POST'])
def guardar_consulta():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        mensaje = request.form.get('mensaje')
        
        if not nombre or not email or not telefono:
            return jsonify({"error": "Nombre, email y teléfono son obligatorios"}), 400
        
        nueva_consulta = Consulta(
            nombre=nombre, 
            email=email, 
            telefono=telefono, 
            mensaje=mensaje
        )
        
        db.session.add(nueva_consulta)
        db.session.commit()
        
        return jsonify({"mensaje": f"¡Gracias {nombre}! Tu consulta fue guardada exitosamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar: {str(e)}"}), 500

# ============================================
# RUTA: CALCULAR FINANCIACIÓN
# ============================================

@app.route('/calcular-cuota', methods=['POST'])
def calcular_cuota():
    try:
        data = request.get_json()
        
        precio_auto = float(data.get('precio', 0))
        anticipo_monto = float(data.get('anticipo', 0))
        cantidad_cuotas = int(data.get('cuotas', 12))
        
        if precio_auto <= 0:
            return jsonify({"error": "El precio debe ser mayor a 0"}), 400
        
        if anticipo_monto < 0:
            return jsonify({"error": "El anticipo no puede ser negativo"}), 400
        
        anticipo_minimo = precio_auto * 0.20
        if anticipo_monto < anticipo_minimo:
            return jsonify({"error": f"El anticipo mínimo es del 20% (USD {anticipo_minimo:,.2f})"}), 400
        
        if anticipo_monto > precio_auto:
            return jsonify({"error": "El anticipo no puede ser mayor al precio del auto"}), 400
        
        monto_a_financiar = precio_auto - anticipo_monto
        valor_cuota = monto_a_financiar / cantidad_cuotas
        
        return jsonify({
            "cuota_mensual": round(valor_cuota, 2),
            "total_financiar": round(monto_a_financiar, 2),
            "anticipo": anticipo_monto,
            "precio": precio_auto,
            "cuotas": cantidad_cuotas
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al calcular: {str(e)}"}), 500

# ============================================
# RUTA: GUARDAR TURNO (MEJORADA CON FINANCIACIÓN)
# ============================================

@app.route('/guardar-turno', methods=['POST'])
def guardar_turno():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        auto_interes = request.form.get('auto_interes')
        mensaje = request.form.get('mensaje')
        
        # Obtener datos de financiación
        precio_auto = request.form.get('precio_auto')
        anticipo = request.form.get('anticipo')
        cuotas = request.form.get('cuotas')
        cuota_mensual = request.form.get('cuota_mensual')
        
        # Validaciones básicas
        if not nombre or not telefono or not fecha or not hora:
            return jsonify({"error": "Nombre, teléfono, fecha y hora son obligatorios"}), 400
        
        # Validar formato de fecha (YYYY-MM-DD)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha):
            return jsonify({"error": "Formato de fecha inválido"}), 400
        
        # Validar formato de hora (HH:MM)
        if not re.match(r'^\d{2}:\d{2}$', hora):
            return jsonify({"error": "Formato de hora inválido"}), 400
        
        # Validar que la fecha no sea pasada
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        if fecha < fecha_actual:
            return jsonify({"error": "La fecha no puede ser anterior a hoy"}), 400
        
        # Limpiar teléfono (solo números)
        telefono_limpio = re.sub(r'\D', '', telefono)
        if len(telefono_limpio) < 8:
            return jsonify({"error": "El teléfono debe tener al menos 8 dígitos"}), 400
        
        # Crear nuevo turno
        nuevo_turno = Turno(
            nombre=nombre,
            telefono=telefono_limpio,
            email=email,
            fecha=fecha,
            hora=hora,
            auto_interes=auto_interes,
            mensaje=mensaje
        )
        
        # Guardar en la base de datos
        db.session.add(nuevo_turno)
        db.session.commit()
        
        # ============================================
        # CONSTRUIR MENSAJE PARA WHATSAPP CON FINANCIACIÓN
        # ============================================
        
        # Formatear fecha para mostrar (DD/MM/YYYY)
        fecha_formateada = datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y')
        
        mensaje_whatsapp = f"""🗓️ *RESERVA DE TURNO - CONCESIONARIA SAN ANDRÉS*

👤 *Cliente:* {nombre}
📱 *Teléfono:* {telefono_limpio}
📧 *Email:* {email or 'No especificado'}

🚗 *Auto de interés:* {auto_interes or 'No especificado'}

📅 *Fecha:* {fecha_formateada}
🕐 *Hora:* {hora}

💬 *Mensaje:* {mensaje or 'Sin mensaje adicional'}

{'='*40}
💰 *SIMULACIÓN DE FINANCIACIÓN*
{'='*40}

"""
        
        # Agregar datos de financiación si existen
        if precio_auto and precio_auto != 'No especificado' and precio_auto != '':
            try:
                # Convertir a números
                precio_float = float(precio_auto)
                anticipo_float = float(anticipo) if anticipo and anticipo != 'No especificado' else 0
                cuotas_int = int(cuotas) if cuotas and cuotas != 'No especificado' else 12
                cuota_float = float(cuota_mensual) if cuota_mensual and cuota_mensual != 'No especificado' else 0
                
                mensaje_whatsapp += f"""
💵 *Precio del auto:* USD ${precio_float:,.2f}
🏦 *Anticipo:* USD ${anticipo_float:,.2f}
💳 *Monto a financiar:* USD ${(precio_float - anticipo_float):,.2f}
📆 *Cuotas:* {cuotas_int} meses
💰 *Cuota mensual:* USD ${cuota_float:,.2f}

✅ *Sin interés* - Plan a medida
"""
            except Exception as e:
                # Si hay error al parsear, mostrar los datos como texto
                mensaje_whatsapp += f"""
💵 *Precio del auto:* USD ${precio_auto}
🏦 *Anticipo:* USD ${anticipo or '0'}
📆 *Cuotas:* {cuotas or '12'}
💰 *Cuota mensual:* USD ${cuota_mensual or 'Calculado al reservar'}
"""
        
        mensaje_whatsapp += f"""

📌 *ID de turno:* #{nuevo_turno.id}
📍 *Dirección:* San Andrés 1661, Buenos Aires
⏰ *Te esperamos!*

_*Este mensaje fue generado automáticamente*_"""
        
        # Codificar para URL de WhatsApp
        mensaje_url = mensaje_whatsapp.replace('\n', '%0A').replace(' ', '%20')
        
        # 🔥 TU NÚMERO DE WHATSAPP CORREGIDO
        whatsapp_url = f"https://wa.me/5491126072201?text={mensaje_url}"
        
        return jsonify({
            "mensaje": f"✅ ¡Turno reservado para {nombre}!",
            "whatsapp_url": whatsapp_url,
            "turno_id": nuevo_turno.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar el turno: {str(e)}"}), 500

# ============================================
# RUTA: VER TURNOS (ADMIN)
# ============================================

@app.route('/turnos')
def ver_turnos():
    turnos = Turno.query.order_by(Turno.fecha.desc(), Turno.hora.asc()).all()
    return render_template('turnos.html', turnos=turnos)

# ============================================
# RUTA: CANCELAR TURNO
# ============================================

@app.route('/cancelar-turno/<int:id>', methods=['POST'])
def cancelar_turno(id):
    try:
        turno = Turno.query.get(id)
        if not turno:
            return jsonify({"error": "Turno no encontrado"}), 404
        
        turno.estado = 'cancelado'
        db.session.commit()
        
        return jsonify({"mensaje": f"Turno #{id} cancelado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al cancelar: {str(e)}"}), 500

# ============================================
# RUTA: CONFIRMAR TURNO
# ============================================

@app.route('/confirmar-turno/<int:id>', methods=['POST'])
def confirmar_turno(id):
    try:
        turno = Turno.query.get(id)
        if not turno:
            return jsonify({"error": "Turno no encontrado"}), 404
        
        turno.estado = 'confirmado'
        db.session.commit()
        
        return jsonify({"mensaje": f"Turno #{id} confirmado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al confirmar: {str(e)}"}), 500

# ============================================
# INICIAR APLICACIÓN
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Base de datos lista")
        print("📊 Tablas creadas: Consulta, Turno")
    print("🚀 Servidor corriendo en http://localhost:5000")
    print("📋 Panel de turnos: http://localhost:5000/turnos")
    app.run(debug=True, host='0.0.0.0', port=5000)
