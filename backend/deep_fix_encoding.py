import os
import glob

def fix_file(filepath):
    try:
        # Önce dosyayı binary olarak oku
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Eğer null byte varsa veya UTF-16 ise düzelt
        if b'\x00' in content:
            print(f"[*] Fixing corrupted file (null bytes detected): {filepath}")
            # UTF-16LE'den UTF-8'e çevirmeyi dene
            try:
                decoded = content.decode('utf-16')
                with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(decoded)
                return True
            except:
                # Eğer UTF-16 değilse ama null byte varsa (gerçek bozulma)
                # Sadece null byte'ları temizle ve UTF-8 olarak kaydet
                decoded = content.replace(b'\x00', b'').decode('utf-8', errors='ignore')
                with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(decoded)
                return True
    except Exception as e:
        print(f"[!] Error processing {filepath}: {e}")
    return False

# Tüm .py dosyalarını tara
base_dir = r'c:\projects\todo\backend'
py_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)

fixed_count = 0
for filepath in py_files:
    if fix_file(filepath):
        fixed_count += 1

print(f"\n[OK] Toplam {fixed_count} dosya temizlendi.")
