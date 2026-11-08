# --- TAMBAHKAN 4 baris ini ke dalam dict VARIANT_TO_KANGXI yang sudah ada ---
# di enrich_leksikon_khusus.py (Lapis 2, translate radikal mentah -> nomor Kangxi baku)
#
# Ditemukan hilang saat melengkapi 25 entri leksikon khusus (BLUEPRINT v26 -> v27):

VARIANT_TO_KANGXI_ADDITIONS = {
    "⺮": 118,  # varian atas dari 竹 (bamboo) - mis. di 算, 笑
    "丷": 12,   # varian atas dari 八 - mis. di 养 (simplified dari 養)
    "贝": 154,  # simplified dari 貝 (kerang/harta) - mis. di 贤
    "门": 169,  # simplified dari 門 (pintu) - mis. di 阁
}

# Cara pasang: cari baris "VARIANT_TO_KANGXI = {" di enrich_leksikon_khusus.py,
# lalu tambahkan 4 baris di atas (key: value) ke dalam dict itu langsung.
# TIDAK perlu jalankan ulang enrichment untuk 470 entri yang sudah ada -
# ini murni pencegahan supaya kata BARU di masa depan dengan radikal ini
# tidak nyangkut kosong lagi.
