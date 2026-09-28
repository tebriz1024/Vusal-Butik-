from fastapi import FastAPI
from fastapi import HTTPException
import bcrypt #i imported because i wanted to add login system but i didnt need it now. you can delete "import bcrypt" :)
import sqlite3
from pydantic import BaseModel
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
conn = sqlite3.connect("vusalbutik.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS elanlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        basliq TEXT NOT NULL,
        qiymet REAL NOT NULL,

        eded INTEGER DEFAULT 1
        )
    """)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sifarisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elan_id INTEGER NOT NULL,
        musteri TEXT NOT NULL,
        eded INTEGER NOT NULL
    )
""")
conn.commit()
conn.close()
class elan_yarat(BaseModel):
    basliq: str
    qiymet: float
    eded: int
class sifaris_yarat(BaseModel):
    musteri: str
    eded: int
#/ ana sehifedi ve tum elanlari gosterir
@app.get("/")
def ana_sehife():
    conn = sqlite3.connect("vusalbutik.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM elanlar""")
    netice = cursor.fetchall()
    conn.close()
    return netice
@app.put("/deyistir/{elan_id}")
def elan_deyistir(elan_id: int, elan: elan_yarat):
    conn = sqlite3.connect("vusalbutik.db")
    cursor = conn.cursor()
    cursor.execute(
    "UPDATE elanlar SET basliq = ?, qiymet = ?, eded = ? WHERE id = ?",
    (elan.basliq, elan.qiymet, elan.eded, elan_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Elan Tapilmadi")
    conn.close()
    return("elan deyistirildi!")
@app.delete("/elansil/{elan_id}")
def elan_sil(elan_id: int):
    conn = sqlite3.connect("vusalbutik.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM elanlar WHERE id = ?", (elan_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Elan Tapilmadi")
    conn.close()
    return {"mesaj": "Elan silindi"}
@app.post("/elanlar")
def elan_elave_et(elan: elan_yarat):
    conn = sqlite3.connect("vusalbutik.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO elanlar (basliq, qiymet, eded) VALUES (?, ?, ?)",
        (elan.basliq, elan.qiymet, elan.eded)
    )
    conn.commit()
    conn.close()
    return {"mesaj": "Elan əlavə olundu"}
@app.post("/elan-sifaris/{elan_id}")
def sifaris_ver(elan_id: int, sifaris: sifaris_yarat):
    conn = sqlite3.connect("vusalbutik.db")
    cursor = conn.cursor()
    cursor.execute("SELECT eded FROM elanlar WHERE id = ?", (elan_id,))
    ededi = cursor.fetchone()
    if ededi is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Elan Tapilmadi")
    if ededi[0] < sifaris.eded:
        conn.close()
        raise HTTPException(status_code=400, detail="Kifayet qeder stok yoxdur")
    cursor.execute(
        "INSERT INTO sifarisler (elan_id, musteri, eded) VALUES (?, ?, ?)",
        (elan_id, sifaris.musteri, sifaris.eded)
    )
    cursor.execute(
        "UPDATE elanlar SET eded = eded - ? WHERE id = ? AND eded >= ?",
        (sifaris.eded, elan_id, sifaris.eded)
    )
    conn.commit()
    conn.close()
    return {"mesaj": "sifaris qeyde alindi"}
@app.on_event("startup")
def startup_event():
    print("Uygulama ve veritabanı başarıyla başlatıldı!")
