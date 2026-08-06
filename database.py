import mysql.connector
import hashlib

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="centro_comercial"
    )

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS local (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero VARCHAR(10) NOT NULL UNIQUE,
            tipo VARCHAR(20) NOT NULL,
            ocupado BOOLEAN DEFAULT TRUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pago (
            id INT AUTO_INCREMENT PRIMARY KEY,
            local_id INT NOT NULL,
            fecha DATE NOT NULL,
            mes VARCHAR(20),
            empresario VARCHAR(150),
            rut VARCHAR(15),
            descripcion VARCHAR(255),
            valor DECIMAL(10,2),
            fecha_pago DATE,
            folio VARCHAR(30) UNIQUE,
            FOREIGN KEY (local_id) REFERENCES local(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def obtener_pagos_por_tipo(tipo, numero_filtro=""):
    conn = conectar()
    cursor = conn.cursor()
    query = """
        SELECT local.numero, pago.fecha, pago.mes, pago.empresario, pago.rut,
               pago.descripcion, pago.valor, pago.fecha_pago, pago.folio
        FROM pago
        JOIN local ON pago.local_id = local.id
        WHERE local.tipo = %s
    """
    params = [tipo]
    if numero_filtro:
        query += " AND local.numero LIKE %s"
        params.append(f"%{numero_filtro}%")
    query += " ORDER BY pago.fecha DESC"

    cursor.execute(query, params)
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


def obtener_o_crear_local(numero, tipo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM local WHERE numero = %s", (numero,))
    resultado = cursor.fetchone()

    if resultado:
        local_id = resultado[0]
    else:
        cursor.execute(
            "INSERT INTO local (numero, tipo, ocupado) VALUES (%s, %s, %s)",
            (numero, tipo, True)
        )
        conn.commit()
        local_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return local_id


def insertar_pago(numero_local, tipo, fecha, mes, empresario, rut, descripcion, valor, fecha_pago, folio):
    local_id = obtener_o_crear_local(numero_local, tipo)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pago (local_id, fecha, mes, empresario, rut, descripcion, valor, fecha_pago, folio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (local_id, fecha, mes, empresario, rut, descripcion, valor, fecha_pago or None, folio))
    conn.commit()
    cursor.close()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def crear_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuario (username, password) VALUES (%s, %s)",
        (username, hash_password(password))
    )
    conn.commit()
    cursor.close()
    conn.close()


def validar_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM usuario WHERE username = %s AND password = %s",
        (username, hash_password(password))
    )
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()
    return resultado is not None
def obtener_locales_desocupados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT numero, tipo FROM local WHERE ocupado = FALSE ORDER BY numero")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


def cambiar_estado_local(numero, ocupado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE local SET ocupado = %s WHERE numero = %s", (ocupado, numero))
    conn.commit()
    cursor.close()
    conn.close()