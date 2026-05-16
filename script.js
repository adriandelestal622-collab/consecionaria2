// ==================== FUNCIONES DE NOTIFICACIÓN ====================

function mostrarToast(mensaje) {
    const toast = document.getElementById('toastNotificacion');
    const mensajeSpan = document.getElementById('toastMensaje');
    mensajeSpan.innerText = mensaje;
    toast.style.display = 'flex';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

// ==================== CONSULTAR AUTO ====================

function consultarAuto(nombre, precio) {
    document.getElementById('mensajeCliente').value = 
        `Hola, quiero información del ${nombre} que cuesta USD ${precio.toLocaleString()}. ¿Está disponible?`;
    document.getElementById('precioAuto').value = precio;
    mostrarToast(`✓ Auto seleccionado: ${nombre}`);
    document.getElementById('formularioContacto').scrollIntoView({ behavior: 'smooth' });
}

// ==================== SIMULADOR DE FINANCIACIÓN ====================

function calcularFinanciacion() {
    // Obtener valores del formulario
    let precio = parseFloat(document.getElementById('precioAuto').value);
    let anticipo = parseFloat(document.getElementById('anticipo').value);
    let cuotas = parseInt(document.getElementById('cuotas').value);
    
    // Cotización del dólar (ACTUALIZAR MANUALMENTE)
    let dolarBlue = 1220; // CAMBIAR SEGÚN COTIZACIÓN
    
    // Validaciones
    if (isNaN(precio) || precio <= 0) {
        mostrarToast("❌ Ingresá un precio válido");
        return;
    }
    
    if (isNaN(anticipo) || anticipo < 0) {
        mostrarToast("❌ Ingresá un anticipo válido");
        return;
    }
    
    let minimoAnticipo = precio * 0.20;
    if (anticipo < minimoAnticipo) {
        mostrarToast(`⚠️ El anticipo mínimo es del 20%: USD ${minimoAnticipo.toLocaleString()}`);
        return;
    }
    
    if (anticipo > precio) {
        mostrarToast("❌ El anticipo no puede ser mayor al precio del auto");
        return;
    }
    
    // Cálculos en DÓLARES
    let financiarUSD = precio - anticipo;
    let cuotaMensualUSD = financiarUSD / cuotas;
    
    // Cálculos en PESOS
    let financiarARS = financiarUSD * dolarBlue;
    let cuotaMensualARS = cuotaMensualUSD * dolarBlue;
    let anticipoARS = anticipo * dolarBlue;
    let precioARS = precio * dolarBlue;
    
    // Mostrar resultado
    let resultadoDiv = document.getElementById('resultadoFinanciacion');
    resultadoDiv.classList.remove('d-none');
    resultadoDiv.innerHTML = `
        <div class="resultado-financiacion">
            <h5><i class="bi bi-check-circle-fill text-success me-2"></i>Tu plan de pagos</h5>
            <div class="row mt-3">
                <div class="col-6 text-center border-end">
                    <small class="text-muted">USD Dólares</small>
                    <p class="fw-bold mb-0">USD ${cuotaMensualUSD.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                    <small>por mes</small>
                </div>
                <div class="col-6 text-center">
                    <small class="text-muted">ARS Pesos</small>
                    <p class="fw-bold mb-0" style="color:#c9a03d;">$${cuotaMensualARS.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</p>
                    <small>por mes</small>
                </div>
            </div>
            <hr>
            <table class="table table-sm table-borderless mt-2">
                <tr><td><strong>💰 Precio:</strong></td><td class="text-end">USD ${precio.toLocaleString()} <span class="text-muted">($${precioARS.toLocaleString()} ARS)</span></td></tr>
                <tr><td><strong>🏦 Anticipo:</strong></td><td class="text-end">USD ${anticipo.toLocaleString()} <span class="text-muted">($${anticipoARS.toLocaleString()} ARS)</span></td></tr>
                <tr><td><strong>💵 Monto a financiar:</strong></td><td class="text-end">USD ${financiarUSD.toLocaleString()} <span class="text-muted">($${financiarARS.toLocaleString()} ARS)</span></td></tr>
                <tr><td><strong>📆 Cuotas:</strong></td><td class="text-end">${cuotas} meses (SIN INTERÉS)</td></tr>
            </table>
            <div class="alert alert-info text-center mt-2 mb-0 py-2">
                <small>💡 Cotización: 1 USD = $${dolarBlue} ARS</small>
            </div>
        </div>
    `;
    
    mostrarToast(`✓ Cuota: USD ${cuotaMensualUSD.toFixed(2)} ($${cuotaMensualARS.toLocaleString()} ARS) por ${cuotas} meses`);
}

// ==================== FORMULARIO DE CONTACTO ====================

document.getElementById('formularioContacto').addEventListener('submit', function(e) {
    e.preventDefault();
    let nombre = document.getElementById('nombreCliente').value.trim();
    let telefono = document.getElementById('telefonoCliente').value.trim();
    let email = document.getElementById('emailCliente').value.trim();
    
    if (!nombre || !telefono || !email) {
        mostrarToast("❌ Completá nombre, teléfono y email");
        return;
    }
    
    mostrarToast(`✅ ¡Gracias ${nombre}! Recibimos tu consulta.`);
    this.reset();
});

// ==================== MODAL DE IMAGEN GRANDE ====================

function verImagenGrande(src) {
    document.getElementById('imageModal').style.display = 'flex';
    document.getElementById('modalImage').src = src;
}

function cerrarImagenGrande() {
    document.getElementById('imageModal').style.display = 'none';
}

// Cerrar modal con tecla ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        cerrarImagenGrande();
    }
});