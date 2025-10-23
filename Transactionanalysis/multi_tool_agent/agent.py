from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from . import tools, prompt

load_dotenv()

transaction_agent = LlmAgent(
    name="transaction_analyzer_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent untuk membaca gambar transaksi, mengekstrak detail, menyimpan ke database, "
        "dan menjalankan query SELECT aman pada tabel 'transactions'."
    ),
    instruction=(
        prompt.PROMPT
        + "\n\n⚠️ Panduan penggunaan tools:\n"
        + "- Gunakan `analisis_transaksi_gambar` untuk menganalisis gambar transaksi dan mengekstrak data seperti tanggal, deskripsi, kategori, jumlah, jenis, metode, dan catatan.\n"
        + "- Gunakan `save_transaction` untuk menyimpan hasil analisis ke database PostgreSQL.\n"
        + "- Gunakan `run_query` hanya untuk menjalankan query SELECT pada tabel 'transactions'.\n"
        + "- Query lain seperti UPDATE, DELETE, INSERT, DROP, ALTER dilarang.\n"
        + "- Query otomatis diberi LIMIT (default 50) untuk keamanan.\n"
        + "Contoh query yang benar: SELECT * FROM transactions WHERE kategori='Makanan';"
    ),
    tools=[
        tools.analisis_transaksi_gambar,
        tools.save_transaction,
        tools.run_query,  
    ],
)

root_agent = transaction_agent



