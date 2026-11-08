import json
import sys

def compare_json_files(file1, file2):
    try:
        with open(file1, 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        with open(file2, 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
        
        if data1 == data2:
            print("✅ Kedua file JSON identik (sama persis)!")
            return True
        else:
            print("❌ File berbeda!")
            
            # Tampilkan perbedaan secara detail
            print("\n📋 Perbedaan yang ditemukan:")
            compare_dict(data1, data2, "")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Error: Salah satu file bukan JSON yang valid - {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Error: File tidak ditemukan - {e}")
        return False

def compare_dict(d1, d2, path=""):
    if type(d1) != type(d2):
        print(f"  {path}: Tipe berbeda ({type(d1).__name__} vs {type(d2).__name__})")
        return
    
    if isinstance(d1, dict):
        all_keys = set(d1.keys()) | set(d2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in d1:
                print(f"  {new_path}: Hanya ada di file 2")
            elif key not in d2:
                print(f"  {new_path}: Hanya ada di file 1")
            else:
                compare_dict(d1[key], d2[key], new_path)
                
    elif isinstance(d1, list):
        if len(d1) != len(d2):
            print(f"  {path}: Panjang list berbeda ({len(d1)} vs {len(d2)})")
        else:
            for i in range(len(d1)):
                compare_dict(d1[i], d2[i], f"{path}[{i}]")
    else:
        if d1 != d2:
            print(f"  {path}: '{d1}' vs '{d2}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_json.py file1.json file2.json")
        sys.exit(1)
    
    compare_json_files(sys.argv[1], sys.argv[2])