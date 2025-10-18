from flask import Flask, render_template, request
from datetime import datetime
import uuid
import math

app = Flask(__name__)

# Catálogo simple
PRODUCTS = [
    {"id": "p1", "name": "Producto A", "price": 7990},
    {"id": "p2", "name": "Producto B", "price": 12990},
    {"id": "p3", "name": "Producto C", "price": 19990},
]

IVA_RATE = 0.19  # Chile

def find_product(product_id: str):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

def clp(n: int | float) -> str:
    """Formatea CLP con miles usando punto y sin decimales."""
    s = f"{int(round(n)):,}"
    return "$ " + s.replace(",", ".")

@app.get("/")
def form():
    return render_template("form.html", products=PRODUCTS, error=None)

@app.post("/boleta")
def boleta():
    product_id = request.form.get("product_id")
    qty = request.form.get("quantity", type=int)
    nombre = request.form.get("nombre", "").strip()
    rut = request.form.get("rut", "").strip().upper()
    email = request.form.get("email", "").strip()
    direccion = request.form.get("direccion", "").strip()

    product = find_product(product_id)
    if not product or not qty or qty <= 0 or not nombre:
        return render_template(
            "form.html",
            products=PRODUCTS,
            error="Revisa los campos obligatorios (producto, cantidad, nombre)."
        )

    unit_price = product["price"]
    neto = unit_price * qty
    iva = math.floor(neto * IVA_RATE + 0.5)
    total = neto + iva

    now = datetime.now()
    boleta_num = f"BOL-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    fecha_hora = now.strftime("%d-%m-%Y %H:%M")

    boleta = {
        "numero": boleta_num,
        "fecha_hora": fecha_hora,
        "cliente": {
            "nombre": nombre,
            "rut": rut,
            "email": email,
            "direccion": direccion
        },
        # usamos 'lineas' (no 'items') para evitar conflicto con dict.items en Jinja
        "lineas": [{
            "descripcion": product["name"],
            "cantidad": qty,
            "precio_unitario": unit_price,
            "subtotal": neto
        }],
        "neto": neto,
        "iva": iva,
        "total": total,
    }

    return render_template("boleta.html", boleta=boleta, clp=clp)

if __name__ == "__main__":
    app.run(debug=True)
