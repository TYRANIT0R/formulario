# Manual de Usuario Sistema Pago Online

## 1. Introducción

Este sistema permite realizar compras de productos tecnológicos de forma rápida y sencilla, seleccionando uno o varios artículos, ingresando datos de cliente, eligiendo boleta o factura y realizando el pago con tarjeta débito o crédito.

El número de tarjeta debe ser válido, por lo que si prefieren usar un número de tarjeta válido sin usar el propio, usar la siguiente página:

https://www.vccgenerator.org/es/result/

---

## 2. Requisitos

- Navegador actualizado.
- Conexión a Internet.
- Tarjeta de débito o crédito.
- RUT válido.

---

## 3. Flujo General del Sistema

1. **Selección de productos**: Puede elegir uno o varios productos disponibles.
2. **Ingreso de datos personales**: Completar con nombre, dirección, RUT y correo electrónico.
3. **Selección de documento**: Elige si desea boleta o factura.
4. **Pago seguro**: Completa los datos de su tarjeta y confirma la transacción (rellenar con datos válidos).
5. **Comprobante**: El sistema genera una boleta o factura electrónica con información de compra.

---

## 4. Pasos Detallados

### 4.1 Seleccionar Productos

- Al ingresar, verá una tabla con productos, precios y stock disponible.
- Marque la casilla de verificación al lado del producto que desea comprar.
- Indique la cantidad deseada (no puede exceder el stock disponible).
- Puede seleccionar más de un producto.

*Nota: Si un producto aparece en gris o con “sin stock”, no podrá seleccionarlo.*

---

### 4.2 Ingresar Datos del Cliente

- Complete su RUT, nombre, dirección y correo electrónico.


---

### 4.3 Elegir Tipo de Documento

- Seleccione Boleta (por defecto) o Factura.

---

### 4.4 Realizar el Pago

- El sistema mostrará un resumen de los productos seleccionados, con precios netos, IVA y total.
- Seleccione el método de pago:
  - Débito
  - Crédito (con opción de cuotas)
- Ingrese:
  - Nombre del titular
  - Número de tarjeta (el sistema formatea automáticamente y detecta la marca)
  - Fecha de vencimiento (MM/AA)
  - CVV (3 o 4 dígitos)

*El sistema valida automáticamente que la tarjeta esté vigente y que el número sea válido.*

---

### 4.5 Confirmación de Compra

- Al confirmar el pago, el sistema:
  - Descuenta el stock de la base de datos.
  - Genera un comprobante (boleta o factura).
  - Muestra la información del pago (tarjeta, cuotas si corresponde, total pagado).

*La boleta o factura puede descargarse o imprimirse directamente desde el navegador.*

---

## 5. Estados del Sistema

| Estado                       | Descripción                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| **Compra exitosa**           | Stock confirmado, pago aceptado, boleta/factura generada.                   |
| **Error de stock**           | Uno de los productos seleccionados ya no tenía stock disponible.            |
| **Error de validación**      | Datos incompletos o tarjeta inválida.                                       |
| **Pago pendiente/fallido**   | Si el pago no fue autorizado por el emisor de la tarjeta.                   |

---

## 6. Preguntas Frecuentes (FAQ)

- **¿Puedo comprar varios productos a la vez?**  
  Sí, basta con marcar varios productos en la tabla de selección.

- **¿Cómo sé si mi compra fue exitosa?**  
  El sistema mostrará la boleta/factura con el número de transacción.

- **¿Qué hago si me quedo sin stock?**  
  Elimina el archivo store.db y vuelve a ejecutar la aplicación

---
