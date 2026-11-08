import pikepdf

INPUT = "file.pdf"
OUTPUT = "unlocked.pdf"

try:
    pdf = pikepdf.open(INPUT)

    pdf.save(OUTPUT)

    print("="*50)
    print("BERHASIL")
    print("File tersimpan :", OUTPUT)

except Exception as e:
    print("GAGAL")
    print(e)