# Manual de Usuario — Sistema Pago Online

## 1. Introducción

Este sistema permite realizar compras de productos tecnológicos de forma rápida y sencilla, seleccionando uno o varios artículos, ingresando datos de cliente, eligiendo boleta o factura y realizando el pago con tarjeta débito o crédito.

---

## 2. Requisitos

- Navegador actualizado (Google Chrome, Edge, Firefox o Safari).
- Conexión a Internet estable.
- Tarjeta de débito o crédito habilitada para pagos online.
- (Opcional) RUT válido si requiere factura.

---

## 3. Flujo General del Sistema

1. **Inicio**: El usuario ingresa a la página principal de compras.
2. **Selección de productos**: Puede elegir uno o varios productos disponibles.
3. **Ingreso de datos personales**: Completa nombre, dirección, RUT (si factura) y correo electrónico.
4. **Selección de documento**: Elige si desea boleta o factura.
5. **Pago seguro**: Completa los datos de su tarjeta y confirma la transacción.
6. **Comprobante**: El sistema genera una boleta o factura electrónica con toda la información.

---

## 4. Pasos Detallados

### 4.1 Seleccionar Productos

- Al ingresar, verá una **tabla con productos, precios y stock disponible**.
- Marque la casilla de verificación al lado del producto que desea comprar.
- Indique la **cantidad** deseada (no puede exceder el stock disponible).
- Puede seleccionar más de un producto.

📝 *Nota: Si un producto aparece en gris o con “sin stock”, no podrá seleccionarlo.*

---

### 4.2 Ingresar Datos del Cliente

- Complete su **RUT** (si desea factura), nombre, dirección y correo electrónico.
- Si elige boleta, el RUT es opcional.
- Si elige factura, el RUT es obligatorio y debe tener formato válido (ej: 12.345.678-5).

📌 *El correo electrónico se usa para enviar el comprobante si la opción está habilitada.*

---

### 4.3 Elegir Tipo de Documento

- Seleccione **Boleta** (por defecto) o **Factura**.
- Si elige factura, el sistema validará automáticamente el RUT.

---

### 4.4 Realizar el Pago

- El sistema mostrará un **resumen de los productos seleccionados**, con precios netos, IVA y total.
- Seleccione el método de pago:
  - 💳 Débito
  - 💳 Crédito (con opción de cuotas)
- Ingrese:
  - Nombre del titular
  - Número de tarjeta (el sistema formatea automáticamente y detecta la marca)
  - Fecha de vencimiento (MM/AA)
  - CVV (3 o 4 dígitos)

🚨 *El sistema valida automáticamente que la tarjeta esté vigente y que el número sea válido (Luhn).*

---

### 4.5 Confirmación de Compra

- Al confirmar el pago, el sistema:
  - Valida que aún haya stock disponible.
  - Descuenta el stock de la base de datos.
  - Genera un comprobante (boleta o factura).
  - Muestra la información del pago (tarjeta, cuotas si corresponde, total pagado).

📄 *La boleta o factura puede descargarse o imprimirse directamente desde el navegador.*

---

## 5. Estados del Sistema

| Estado                  | Descripción                                                                 |
|--------------------------|------------------------------------------------------------------------------|
| ✅ **Compra exitosa**            | Stock confirmado, pago aceptado, boleta/factura generada.                    |
| ⚠️ **Error de stock**           | Uno de los productos seleccionados ya no tenía stock disponible.            |
| ❌ **Error de validación**      | Datos incompletos o tarjeta inválida.                                       |
| 🕒 **Pago pendiente/fallido**   | Si el pago no fue autorizado por el emisor de la tarjeta.                   |

---

## 6. Preguntas Frecuentes (FAQ)

- **¿Puedo comprar varios productos a la vez?**  
  ✔️ Sí, basta con marcar varios productos en la tabla de selección.

- **¿Qué pasa si no tengo RUT?**  
  Puede elegir boleta y dejar ese campo en blanco.

- **¿Cómo sé si mi compra fue exitosa?**  
  El sistema mostrará un mensaje de confirmación y la boleta/factura con el número de transacción.

- **¿Puedo usar una tarjeta extranjera?**  
  Depende de la pasarela de pago habilitada en la versión en producción.

---

## 7. Contacto y Soporte

📧 soporte@tuempresa.cl  
📞 +56 9 1234 5678  
📍 Santiago, Chile

---

## 8. Generar PDF (Opcional)

Puedes generar este manual como PDF si usas WeasyPrint:

```bash
weasyprint manual_usuario.md manual_usuario.pdf
```

📌 También puedes integrarlo como una sección accesible en `/manual` dentro del sistema.
