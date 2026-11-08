"""
translate_theme_labels.py
Jalankan : python translate_theme_labels.py
Output   : C:\mandarin_app\data\index_theme.json  (diupdate in-place)
Backup   : C:\mandarin_app\data\index_theme_backup.json

Mengganti label_id pada 119 tema ext_ yang masih berbahasa Inggris
dengan terjemahan Bahasa Indonesia. Label yang sudah berbahasa Indonesia
(38 tema internal) tidak disentuh.
"""

import json, pathlib, shutil

THEME_FILE   = pathlib.Path(r"C:\mandarin_app\data\index_theme.json")
BACKUP_FILE  = pathlib.Path(r"C:\mandarin_app\data\index_theme_backup.json")

# ── Kamus terjemahan lengkap (119 tema ext_) ───────────────────
TERJEMAHAN = {
    # ── Tanpa prefix "HSK ... Vocabulary List" ──
    "ext_careers":                                   "Karier & Profesi",
    "ext_chinese_apps":                              "Aplikasi Mandarin",
    "ext_colors":                                    "Warna (Ext)",
    "ext_commonly_used_spoken_words":                "Kata Percakapan Umum",
    "ext_relatives":                                 "Sanak Saudara",
    "ext_shenfenguanxi":                             "Status & Hubungan (身份关系)",

    # ── Dengan prefix "HSK ... Vocabulary List" ──
    "ext_alcohol":                                   "Minuman Keras & Alkohol",
    "ext_allergy":                                   "Alergi",
    "ext_animals":                                   "Hewan (HSK)",
    "ext_ball_games":                                "Olahraga Bola",
    "ext_beverage":                                  "Minuman",
    "ext_birthday":                                  "Ulang Tahun",
    "ext_body_parts":                                "Bagian Tubuh",
    "ext_buy_fruit":                                 "Membeli Buah",
    "ext_car_related":                               "Otomotif & Mobil",
    "ext_children_s_day_childhood":                  "Hari Anak & Masa Kecil",
    "ext_china_cities":                              "Kota-kota di Tiongkok",
    "ext_chinese_idioms":                            "Idiom Mandarin (成语)",
    "ext_christmas":                                 "Natal",
    "ext_cleaning":                                  "Kebersihan & Bersih-bersih",
    "ext_clothing":                                  "Pakaian & Busana",
    "ext_coffee":                                    "Kopi",
    "ext_cold_weather_staying_warm":                 "Cuaca Dingin & Kehangatan",
    "ext_comfort_food_in_winter":                    "Makanan Hangat Musim Dingin",
    "ext_computer_operation":                        "Operasi Komputer",
    "ext_condiment":                                 "Bumbu & Rempah",
    "ext_cooking_method":                            "Metode Memasak",
    "ext_covid_19":                                  "COVID-19 & Pandemi",
    "ext_currency":                                  "Mata Uang",
    "ext_dating":                                    "Kencan & Percintaan",
    "ext_demonstrative_pronoun":                     "Kata Ganti Penunjuk",
    "ext_directions":                                "Arah & Petunjuk Jalan",
    "ext_dragon_boat_festival_traditions":           "Festival Perahu Naga & Tradisi",
    "ext_early_summer_vibes":                        "Suasana Awal Musim Panas",
    "ext_earth_day_environment":                     "Hari Bumi & Lingkungan",
    "ext_easter_spring_traditions":                  "Paskah & Tradisi Musim Semi",
    "ext_education":                                 "Pendidikan",
    "ext_electronic_product":                        "Produk Elektronik",
    "ext_emotion":                                   "Emosi & Perasaan",
    "ext_farewell_to_the_old_welcome_the_new":       "Selamat Tinggal Tahun Lama",
    "ext_fast_food":                                 "Makanan Cepat Saji",
    "ext_father_s_day":                              "Hari Ayah",
    "ext_festival":                                  "Festival & Perayaan",
    "ext_film_and_television":                       "Film & Televisi",
    "ext_flavor":                                    "Rasa & Cita Rasa",
    "ext_flower":                                    "Bunga",
    "ext_frequency_of_occurrence":                   "Frekuensi Kejadian",
    "ext_fruit":                                     "Buah-buahan (HSK)",
    "ext_furniture":                                 "Perabot Rumah",
    "ext_go_travelling":                             "Bepergian & Wisata",
    "ext_graduation_school_life":                    "Kelulusan & Kehidupan Sekolah",
    "ext_greetings":                                 "Sapaan & Salam",
    "ext_haircut":                                   "Potong Rambut & Salon",
    "ext_halloween":                                 "Halloween",
    "ext_hand_movements":                            "Gerakan Tangan",
    "ext_hanukkah":                                  "Hanukkah",
    "ext_hobby":                                     "Hobi & Waktu Luang",
    "ext_hotel_related":                             "Perhotelan",
    "ext_hsk_summer_vacation_begins":                "Liburan Musim Panas Dimulai",
    "ext_injure":                                    "Cedera & Luka",
    "ext_interrogative_pronoun":                     "Kata Tanya",
    "ext_job_interview":                             "Wawancara Kerja",
    "ext_labor_and_craftsmanship":                   "Buruh & Kerajinan Tangan",
    "ext_language":                                  "Bahasa",
    "ext_lantern_festival_light_culture":            "Festival Lampion & Budaya Cahaya",
    "ext_meat":                                      "Daging",
    "ext_month_and_season":                          "Bulan & Musim",
    "ext_morning_routine":                           "Rutinitas Pagi",
    "ext_mother_s_day":                              "Hari Ibu",
    "ext_movie_type":                                "Genre Film",
    "ext_music_type":                                "Genre Musik",
    "ext_musical_instrument":                        "Alat Musik",
    "ext_names_of_stationery":                       "Alat Tulis",
    "ext_names_of_the_currency":                     "Nama Mata Uang",
    "ext_names_of_the_main_countries":               "Nama Negara Utama",
    "ext_national_leader":                           "Pemimpin Negara",
    "ext_new_year_resolutions":                      "Tahun Baru & Resolusi",
    "ext_numeral":                                   "Angka & Bilangan",
    "ext_office":                                    "Kantor",
    "ext_personal_pronouns":                         "Kata Ganti Orang",
    "ext_physical_appearances":                      "Penampilan Fisik",
    "ext_places":                                    "Tempat & Lokasi",
    "ext_preparing_for_the_new_year":                "Persiapan Tahun Baru",
    "ext_pride_month":                               "Pride Month",
    "ext_qingming_festival_remembrance":             "Festival Qingming & Peringatan",
    "ext_rain_and_solar_terms":                      "Hujan & Istilah Kalender Surya",
    "ext_religion":                                  "Agama & Kepercayaan",
    "ext_restaurant":                                "Restoran",
    "ext_school_life_semester_start":                "Kehidupan Sekolah & Awal Semester",
    "ext_school":                                    "Sekolah",
    "ext_sexual_identity":                           "Identitas Seksual",
    "ext_shapes":                                    "Bentuk & Bangun",
    "ext_sick":                                      "Sakit & Penyakit",
    "ext_sports":                                    "Olahraga",
    "ext_spring_nature":                             "Musim Semi & Alam",
    "ext_spring_and_flowers":                        "Musim Semi & Bunga",
    "ext_spring_festival_reunion":                   "Festival Musim Semi & Reuni",
    "ext_spring_festivals_flowers":                  "Festival & Bunga Musim Semi",
    "ext_spring_outings":                            "Piknik & Jalan-jalan Musim Semi",
    "ext_st_patrick_s_day":                          "Hari St. Patrick",
    "ext_staple_food":                               "Makanan Pokok",
    "ext_summer_holiday_essentials":                 "Perlengkapan Liburan Musim Panas",
    "ext_summer_vacation_begins":                    "Liburan Musim Panas",
    "ext_summer":                                    "Musim Panas",
    "ext_tableware":                                 "Peralatan Makan",
    "ext_the_beginning_of_spring":                   "Awal Musim Semi (立春)",
    "ext_time":                                      "Waktu & Jam",
    "ext_tree_planting_environmental_awareness":     "Menanam Pohon & Kesadaran Lingkungan",
    "ext_valentine_s_day":                           "Hari Valentine",
    "ext_vegetables":                                "Sayuran (HSK)",
    "ext_vehicle":                                   "Kendaraan",
    "ext_video_games":                               "Video Game",
    "ext_weather_and_seasons":                       "Cuaca & Musim",
    "ext_weather":                                   "Cuaca",
    "ext_winter_activities":                         "Aktivitas Musim Dingin",
    "ext_winter_life":                               "Kehidupan Musim Dingin",
    "ext_women_and_family":                          "Wanita & Keluarga",
    "ext_women_s_history_month":                     "Bulan Sejarah Wanita",
    "ext_youth_and_campus_life":                     "Kehidupan Kampus & Pemuda",
}

# ── Load ───────────────────────────────────────────────────────
with open(THEME_FILE, encoding="utf-8") as f:
    data = json.load(f)

# ── Backup dulu ────────────────────────────────────────────────
shutil.copy(THEME_FILE, BACKUP_FILE)
print(f"Backup disimpan → {BACKUP_FILE.name}")

# ── Update label_id ────────────────────────────────────────────
diupdate  = 0
tidak_ada = []

for key, label_id_baru in TERJEMAHAN.items():
    if key in data:
        lama = data[key].get("label_id", "")
        data[key]["label_id"] = label_id_baru
        print(f"  ✓  {key:<50}  '{lama}'  →  '{label_id_baru}'")
        diupdate += 1
    else:
        tidak_ada.append(key)

# ── Simpan ─────────────────────────────────────────────────────
with open(THEME_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ── Laporan ────────────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"Label berhasil diupdate : {diupdate} / {len(TERJEMAHAN)}")
if tidak_ada:
    print(f"Key tidak ditemukan di JSON ({len(tidak_ada)}):")
    for k in tidak_ada:
        print(f"  - {k}")
print(f"\n✓ Disimpan ke: {THEME_FILE}")
print(f"  Backup tersedia di: {BACKUP_FILE}")
print("\nCek hasil: buka index_theme.json dan cari beberapa key ext_")
print("untuk memastikan label_id sudah berubah ke Bahasa Indonesia.")
