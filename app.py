from flask import Flask, render_template, request
from datetime import datetime
import uuid
import math
import re
from email.utils import parseaddr

app = Flask(__name__)

PRODUCTS = [
    {"id": "p1", "name": "Producto A", "price": 7990},
    {"id": "p2", "name": "Producto B", "price": 12990},
    {"id": "p3", "name": "Producto C", "price": 19990},
]

IVA_RATE = 0.19

def calc_dv_rut(num_str: str) -> str:
    m = 2
    s = 0
    for d in reversed(num_str):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    if r == 11:
        return "0"
    if r == 10:
        return "K"
    return str(r)

def validar_rut(rut: str) -> bool:
    if not rut:
        return False
    rut = rut.strip().upper().replace(".", "")
    if "-" not in rut:
        return False
    cuerpo, dv = rut.split("-", 1)
    if not cuerpo.isdigit() or not dv:
        return False
    return calc_dv_rut(cuerpo) == dv

def validar_email(email: str) -> bool:
    if not email:
        return True
    _, addr = parseaddr(email)
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", addr))

def clp(n: int | float) -> str:
    s = f"{int(round(n)):,}"
    return "$ " + s.replace(",", ".")

def find_product(product_id: str):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

@app.get("/")
def form():
    return render_template("form.html", products=PRODUCTS, errors=None, formdata={"tipo_doc": "boleta"})

@app.post("/boleta")
def emitir():
    formdata = {
        "tipo_doc": (request.form.get("tipo_doc") or "boleta").lower(),
        "product_id": request.form.get("product_id"),
        "quantity": request.form.get("quantity", type=int),
        "nombre": (request.form.get("nombre") or "").strip(),
        "rut": (request.form.get("rut") or "").strip(),
        "email": (request.form.get("email") or "").strip(),
        "direccion": (request.form.get("direccion") or "").strip(),
    }

    errors = []

    if formdata["tipo_doc"] not in ("boleta", "factura"):
        errors.append("Selecciona Boleta o Factura.")

    product = find_product(formdata["product_id"])
    if not product:
        errors.append("Selecciona un producto válido.")

    qty = formdata["quantity"]
    if not qty or qty < 1:
        errors.append("La cantidad debe ser un entero mayor o igual a 1.")

    nombre = formdata["nombre"]
    if len(nombre) < 3 or len(nombre) > 80:
        errors.append("El nombre debe tener entre 3 y 80 caracteres.")

    direccion = formdata["direccion"]
    if len(direccion) < 5:
        errors.append("La dirección es obligatoria (mínimo 5 caracteres).")

    rut = formdata["rut"]
    if formdata["tipo_doc"] == "factura":
        if not rut or not validar_rut(rut):
            errors.append("Para Factura el RUT es obligatorio y debe ser válido.")
    else:
        if rut and not validar_rut(rut):
            errors.append("RUT inválido. Usa formato 12.345.678-5.")

    email = formdata["email"]
    if email and not validar_email(email):
        errors.append("Email inválido (ej: correo@dominio.cl).")

    if errors:
        return render_template("form.html", products=PRODUCTS, errors=errors, formdata=formdata)

    unit_price = product["price"]
    neto = unit_price * qty
    iva = math.floor(neto * IVA_RATE + 0.5)
    total = neto + iva

    now = datetime.now()
    pref = "BOL" if formdata["tipo_doc"] == "boleta" else "FAC"
    numero = f"{pref}-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    fecha_hora = now.strftime("%d-%m-%Y %H:%M")

    doc = {
        "tipo": "Boleta" if formdata["tipo_doc"] == "boleta" else "Factura",
        "numero": numero,
        "fecha_hora": fecha_hora,
        "cliente": {
            "nombre": nombre,
            "rut": rut.upper(),
            "email": email,
            "direccion": direccion,
        },
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

    tpl = "boleta.html" if formdata["tipo_doc"] == "boleta" else "factura.html"
    return render_template(tpl, doc=doc, clp=clp)

if __name__ == "__main__":
    app.run(debug=True)
