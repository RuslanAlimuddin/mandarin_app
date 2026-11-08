import PyPDF2
import re
import os

# --- KONFIGURASI ---
# Ganti 'nama_file_anda.pdf' dengan nama file PDF Anda
INPUT_PDF = "新版HSK考试大纲1219.pdf"

# Daftar bagian yang ingin diekstrak. Format: (Nama_Bagian, String_Pencarian)
# String pencarian adalah teks unik yang menandai awal dan akhir bagian
SECTIONS = [
    ("HSK1", "HSK（一级）语法"),
    ("HSK2", "HSK（二级）语法"),
    ("HSK3", "HSK（三级）语法"),
    ("HSK4", "HSK（四级）语法"),
    ("HSK5", "HSK（五级）语法"),
    ("HSK6", "HSK（六级）语法"),
    ("HSK7-9", "HSK（七—九级）语法"),
]
# -----------------

def extract_section(pdf_path, start_marker, end_marker):
    """
    Mengekstrak teks dari PDF antara dua marker.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            found_start = False

            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Periksa apakah marker awal ditemukan di halaman ini
                if not found_start:
                    if start_marker in text:
                        found_start = True
                        # Mulai dari posisi marker
                        start_index = text.find(start_marker)
                        full_text += text[start_index:]
                else:
                    # Jika sudah menemukan awal, tambahkan semua teks
                    full_text += text
                
                # Jika sudah menemukan akhir, berhenti
                if found_start and end_marker in text and end_marker != start_marker:
                    # Potong teks sampai akhir marker
                    end_index = text.find(end_marker) + len(end_marker)
                    full_text = full_text[:-len(text) + end_index]
                    break

            if not found_start:
                print(f"Peringatan: Marker awal '{start_marker}' tidak ditemukan.")

            return full_text
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' tidak ditemukan. Pastikan file ada di folder yang sama.")
        return None
    except Exception as e:
        print(f"Terjadi kesalahan saat memproses PDF: {e}")
        return None

def main():
    # Buat folder 'output' jika belum ada
    if not os.path.exists("output"):
        os.makedirs("output")

    print(f"Memproses file: {INPUT_PDF}\n")
    
    for i, (section_name, start_marker) in enumerate(SECTIONS):
        # Tentukan end_marker. Untuk bagian terakhir, gunakan marker yang tidak mungkin ditemukan (atau EOF).
        if i + 1 < len(SECTIONS):
            end_marker = SECTIONS[i+1][1]
        else:
            # Untuk bagian terakhir, gunakan string yang tidak ada
            end_marker = "---AKHIR_DOKUMEN---"

        print(f"-> Mengekstrak: {section_name} (Mulai: '{start_marker}')")
        extracted_text = extract_section(INPUT_PDF, start_marker, end_marker)

        if extracted_text:
            output_filename = f"output/{section_name}.txt"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"   Berhasil disimpan ke: {output_filename}")
        else:
            print(f"   Gagal mengekstrak {section_name}.")
        print("-" * 30)

    print("\nProses ekstraksi selesai! File teks tersimpan di folder 'output'.")

if __name__ == "__main__":
    main()