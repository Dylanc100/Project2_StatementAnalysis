import psycopg2
import os
from decimal import Decimal
from google import genai


def analisis_transaksi_gambar(file_path: str) -> dict:
    """
    Analisis gambar transaksi (dengan path file, bukan bytes).
    """
    try:
        #Validasi file
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"File '{file_path}' tidak ditemukan. Pastikan file tersedia dan dapat diakses."
            }

        client = genai.Client()

        # Baca file lokal
        with open(file_path, "rb") as f:
            image_data = f.read()

        # Kirim ke model Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": (
                            "Analisis gambar ini dan ekstrak informasi transaksi seperti "
                            "tanggal, deskripsi, kategori, sub_kategori, jumlah, jenis, metode, dan catatan."
                        )},
                        {"inline_data": {"mime_type": "image/png", "data": image_data}},
                    ],
                }
            ],
        )

        result = response.candidates[0].content.parts[0].text
        return {"status": "success", "result": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_transaction(
    tanggal: str,
    deskripsi: str,
    kategori: str,
    sub_kategori: str,
    jumlah: float,
    jenis: str,
    metode: str,
    catatan: str,
) -> dict:
    """
    Menyimpan hasil analisis transaksi ke PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            dbname="Transactionchecking",
            user="postgres",
            password="moing1",
            host="localhost",
            port="5432",
        )
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO transactions (tanggal, deskripsi, kategori, sub_kategori, jumlah, jenis, metode, catatan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (tanggal, deskripsi, kategori, sub_kategori, jumlah, jenis, metode, catatan),
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "Transaksi berhasil disimpan."}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_query(query: str, limit: int = 50) -> dict:
    """
    Menjalankan query SELECT aman pada tabel 'transactions' dengan batas limit.
    Hanya mengizinkan SELECT pada tabel 'transactions'.
    """
    try:
        # Validasi keamanan query
        q_lower = query.strip().lower()
        if not q_lower.startswith("select"):
            return {"status": "error", "message": "Hanya query SELECT yang diperbolehkan."}
        if "transactions" not in q_lower:
            return {"status": "error", "message": "Query hanya boleh pada tabel 'transactions'."}

        # Pastikan pakai LIMIT
        if "limit" not in q_lower:
            query = f"{query.strip()} LIMIT {limit}"

        # Ganti fungsi tanggal agar sesuai PostgreSQL (bukan SQLite)
        query = query.replace("date('now', '-30 days')", "CURRENT_DATE - INTERVAL '30 days'")

        # Koneksi PostgreSQL
        conn = psycopg2.connect(
            dbname="Transactionchecking",
            user="postgres",
            password="moing1",
            host="localhost",
            port="5432",
        )
        cur = conn.cursor()

        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Ubah hasil ke bentuk JSON-friendly
        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            for key, value in row_dict.items():
                # Konversi tipe data yang tidak bisa di-serialize
                if isinstance(value, Decimal):
                    row_dict[key] = float(value)
                elif hasattr(value, "strftime"):  # Tanggal -> string
                    row_dict[key] = value.strftime("%Y-%m-%d")
            results.append(row_dict)

        return {"status": "success", "results": results}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    





