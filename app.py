from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import uuid
import re
from email.utils import parseaddr
from sqlalchemy import (create_engine, Column, String, Integer, DateTime,
                        select, update, func)
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)
app.secret_key = "cambia-esto-por-una-clave-segura"

engine = create_engine("sqlite:///store.db", future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, future=True, expire_on_commit=False)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True)    
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)   
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), default=func.now())

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        cnt = db.scalar(select(func.count()).select_from(Product))
        if cnt == 0:
            seed = [
                Product(id="p1",  name="Notebook Lenovo IdeaPad 3",                   price=429990, stock=5),
                Product(id="p2",  name="iPhone 17 Pro 128GB",                         price=999990, stock=4),
                Product(id="p3",  name="Smart TV Samsung 55'' 4K UHD",               price=379990, stock=6),
                Product(id="p4",  name="Audífonos Inalámbricos Sony WH-1000XM5",     price=299990, stock=8),
                Product(id="p5",  name="Mouse Gamer Logitech G Pro X Superlight 2",  price=179990, stock=10),
                Product(id="p6",  name="Teclado Mecánico Redragon Kumara RGB",       price=49990,  stock=15),
                Product(id="p7",  name="Monitor Asus 27'' Full HD 240Hz",            price=189990, stock=7),
                Product(id="p8",  name="Tablet Samsung Galaxy Tab S10 128GB",        price=349990, stock=6),
                Product(id="p9",  name="Disco SSD Kingston NV2 1TB NVMe",            price=67990,  stock=20),
                Product(id="p10", name="Router Wi-Fi 6 TP-Link AX1800",              price=59990,  stock=12),
            ]
            db.add_all(seed)
            db.commit()


init_db()

IVA_RATE = 0.19

def calc_dv_rut(num_str: str) -> str:
    m, s = 2, 0
    for d in reversed(num_str):
        s += int(d) * m
        m = 2 if m == 7 else m + 1
    r = 11 - (s % 11)
    return "0" if r == 11 else ("K" if r == 10 else str(r))

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
    if not email:  # opcional
        return True
    _, addr = parseaddr(email)
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", addr))

def clp(n: int | float) -> str:
    s = f"{int(round(n)):,}"
    return "$ " + s.replace(",", ".")

def luhn_ok(number: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", number)]
    if not digits:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

def guess_brand(number: str) -> str:
    n = re.sub(r"\D", "", number)
    if n.startswith("4"): return "VISA"
    if re.match(r"^5[1-5]", n) or re.match(r"^(222[1-9]|22[3-9]\d|2[3-6]\d{2}|27[01]\d|2720)", n): return "Mastercard"
    if re.match(r"^3[47]", n): return "AMEX"
    return "Tarjeta"

def parse_mm_yy(venc: str):
    m = re.match(r"^\s*(\d{2})\s*/\s*(\d{2})\s*$", venc or "")
    if not m: return None, None
    mm, yy = int(m.group(1)), int(m.group(2))
    if not (1 <= mm <= 12): return None, None
    return mm, 2000 + yy

def totales_from_items(items):
    total = sum(it["subtotal"] for it in items)
    neto = round(total / (1 + IVA_RATE))
    iva = total - neto
    return neto, iva, total

@app.get("/")
def form():
    with SessionLocal() as db:
        products = db.scalars(select(Product).order_by(Product.name)).all()
        products_ctx = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in products]
    return render_template(
        "form.html",
        products=products_ctx,
        errors=None,
        formdata=session.get("cliente_form") or {"tipo_doc": "boleta"},
        clp=clp
    )

@app.post("/pagos")
def continuar_a_pagos():
    tipo = (request.form.get("tipo_doc") or "boleta").lower()

    selected_ids = request.form.getlist("product_ids")
    qty_by_id = {}
    for pid in selected_ids:
        qty_raw = request.form.get(f"qty[{pid}]")
        try:
            qty_by_id[pid] = int(qty_raw)
        except:
            qty_by_id[pid] = 0

    formdata = {
        "tipo_doc": tipo,
        "nombre": (request.form.get("nombre") or "").strip(),
        "rut": (request.form.get("rut") or "").strip(),
        "email": (request.form.get("email") or "").strip(),
        "direccion": (request.form.get("direccion") or "").strip(),
    }

    errors = []
    if tipo not in ("boleta", "factura"):
        errors.append("Selecciona Boleta o Factura.")

    items = []
    if not selected_ids:
        errors.append("Selecciona al menos un producto.")
    else:
        with SessionLocal() as db:
            products = db.scalars(select(Product).where(Product.id.in_(selected_ids))).all()
            prod_map = {p.id: p for p in products}
            for pid in selected_ids:
                prod = prod_map.get(pid)
                if not prod:
                    errors.append(f"Producto {pid} inválido.")
                    continue
                qty = qty_by_id.get(pid, 0)
                if qty < 1:
                    errors.append(f"La cantidad de {prod.name} debe ser >= 1.")
                    continue
                if qty > prod.stock:
                    errors.append(f"Sin stock suficiente para {prod.name}. Disponible: {prod.stock}.")
                    continue
                items.append({
                    "id": pid,
                    "descripcion": prod.name,
                    "cantidad": qty,
                    "precio_unitario": prod.price,
                    "subtotal": prod.price * qty
                })

    nombre = formdata["nombre"]
    if len(nombre) < 3 or len(nombre) > 80:
        errors.append("El nombre debe tener entre 3 y 80 caracteres.")
    direccion = formdata["direccion"]
    if len(direccion) < 5:
        errors.append("La dirección es obligatoria (mínimo 5 caracteres).")
    rut = formdata["rut"]
    if tipo == "factura":
        if not rut or not validar_rut(rut):
            errors.append("Para Factura el RUT es obligatorio y debe ser válido.")
    else:
        if rut and not validar_rut(rut):
            errors.append("RUT inválido. Usa formato 12.345.678-5.")
    email = formdata["email"]
    if email and not validar_email(email):
        errors.append("Email inválido (ej: correo@dominio.cl).")

    if errors:
        formdata_return = {"tipo_doc": tipo, **formdata}
        formdata_return["selected_ids"] = selected_ids
        formdata_return["qty"] = {pid: request.form.get(f"qty[{pid}]") for pid in selected_ids}
        with SessionLocal() as db:
            products = db.scalars(select(Product).order_by(Product.name)).all()
            products_ctx = [{"id": p.id, "name": p.name, "price": p.price, "stock": p.stock} for p in products]
        return render_template("form.html", products=products_ctx, errors=errors, formdata=formdata_return, clp=clp)

    session["cliente_form"] = {**formdata, "items": items}
    return redirect(url_for("pagos"))

@app.get("/pagos")
def pagos():
    formdata = session.get("cliente_form")
    if not formdata:
        return redirect(url_for("form"))
    neto, iva, total = totales_from_items(formdata["items"])
    resumen = {"items": formdata["items"], "neto": neto, "iva": iva, "total": total}
    return render_template("pagos.html", formdata=formdata, resumen=resumen, clp=clp)

@app.post("/pagar")
def pagar():
    formdata = session.get("cliente_form")
    if not formdata:
        return redirect(url_for("form"))

    metodo = (request.form.get("metodo") or "").lower()
    titular = (request.form.get("titular") or "").strip()
    numero = (request.form.get("numero") or "").strip()
    vencimiento = (request.form.get("vencimiento") or "").strip()
    cvv = (request.form.get("cvv") or "").strip()
    cuotas = request.form.get("cuotas", type=int) if request.form.get("cuotas") else None

    errors = []
    if metodo not in ("debito", "credito"):
        errors.append("Selecciona Débito o Crédito.")
    if len(titular) < 3:
        errors.append("Nombre del titular inválido.")

    num_digits = re.sub(r"\D", "", numero)
    if len(num_digits) < 13 or len(num_digits) > 19 or not luhn_ok(num_digits):
        errors.append("Número de tarjeta inválido.")

    mm, yyyy = parse_mm_yy(vencimiento)
    if not mm:
        errors.append("Vencimiento inválido. Usa formato MM/AA.")
    else:
        now = datetime.now()
        if (yyyy < now.year) or (yyyy == now.year and mm < now.month):
            errors.append("La tarjeta está vencida.")

    if not re.match(r"^\d{3,4}$", cvv or ""):
        errors.append("CVV inválido.")
    if metodo == "credito":
        if cuotas is None or cuotas not in (2, 3, 4, 6, 12):
            errors.append("Selecciona cuotas válidas (2, 3, 4, 6, 12).")
    else:
        cuotas = None

    items = formdata.get("items", [])
    if not items:
        errors.append("No hay productos en el carrito.")

    if not errors:
        with SessionLocal() as db:
            prod_map = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_([it["id"] for it in items]))).all()}
            for it in items:
                p = prod_map.get(it["id"])
                if not p or it["cantidad"] > p.stock:
                    errors.append(f"El stock de {it['descripcion']} cambió. Disponible ahora: {p.stock if p else 0}.")
                    break

    if errors:
        neto, iva, total = totales_from_items(items) if items else (0,0,0)
        resumen = {"items": items, "neto": neto, "iva": iva, "total": total}
        return render_template("pagos.html", formdata=formdata, resumen=resumen, clp=clp, errors=errors,
                               pago_prev={"metodo": metodo, "titular": titular, "numero": numero,
                                          "vencimiento": vencimiento, "cuotas": cuotas})

    with SessionLocal() as db:
        try:
            for it in items:
                stmt = (
                    update(Product)
                    .where(Product.id == it["id"], Product.stock >= it["cantidad"])
                    .values(stock=Product.stock - it["cantidad"], updated_at=func.now())
                )
                res = db.execute(stmt)
                if res.rowcount == 0:
                    raise RuntimeError(f"Sin stock suficiente para {it['descripcion']}.")
            db.commit()
        except Exception as e:
            db.rollback()
            errors.append(str(e))

    if errors:
        neto, iva, total = totales_from_items(items) if items else (0,0,0)
        resumen = {"items": items, "neto": neto, "iva": iva, "total": total}
        return render_template("pagos.html", formdata=formdata, resumen=resumen, clp=clp, errors=errors,
                               pago_prev={"metodo": metodo, "titular": titular, "numero": numero,
                                          "vencimiento": vencimiento, "cuotas": cuotas})

    auth_code = uuid.uuid4().hex[:8].upper()
    brand = guess_brand(num_digits)
    last4 = num_digits[-4:]

    now = datetime.now()
    pref = "FAC" if formdata["tipo_doc"] == "factura" else "BOL"
    numero_doc = f"{pref}-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    fecha_hora = now.strftime("%d-%m-%Y %H:%M")

    neto, iva, total = totales_from_items(items)

    doc = {
        "tipo": "Factura" if formdata["tipo_doc"] == "factura" else "Boleta",
        "numero": numero_doc,
        "fecha_hora": fecha_hora,
        "cliente": {
            "nombre": formdata["nombre"],
            "rut": formdata["rut"].upper(),
            "email": formdata["email"],
            "direccion": formdata["direccion"],
        },
        "lineas": items,
        "neto": neto,
        "iva": iva,
        "total": total,
        "pago": {
            "metodo": "Crédito" if metodo == "credito" else "Débito",
            "marca": brand,
            "last4": last4,
            "cuotas": cuotas,
            "autorizacion": auth_code
        }
    }

    session.pop("cliente_form", None)
    tpl = "factura.html" if formdata["tipo_doc"] == "factura" else "boleta.html"
    return render_template(tpl, doc=doc, clp=clp)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
