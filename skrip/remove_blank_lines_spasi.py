from pathlib import Path

# =====================================================
# PENGATURAN
# =====================================================

input_file = "PILAR 11.txt"          # File sumber
output_file = "PILAR 11_clean.txt"   # File hasil

# =====================================================
# PROSES
# =====================================================

input_path = Path(input_file)

if not input_path.exists():
    print(f"File tidak ditemukan: {input_file}")
    exit()

with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

clean_lines = [line for line in lines if line.strip()]

with open(output_file, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(clean_lines)

print("=" * 40)
print("SELESAI")
print(f"File asal : {input_file}")
print(f"File baru : {output_file}")
print(f"Baris awal : {len(lines)}")
print(f"Baris akhir: {len(clean_lines)}")
print(f"Baris kosong dihapus: {len(lines) - len(clean_lines)}")
print("=" * 40)