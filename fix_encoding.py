import os
import glob

models_path = r'c:\projects\todo\backend\api\models'
files = glob.glob(os.path.join(models_path, '*.py'))

for filepath in files:
    try:
        # Try reading as UTF-16LE first
        with open(filepath, 'r', encoding='utf-16-le') as f:
            content = f.read()
        
        # Write back as UTF-8
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✓ Fixed: {os.path.basename(filepath)}")
    except UnicodeDecodeError:
        # File is already UTF-8 or different encoding
        print(f"- Skipped (already UTF-8): {os.path.basename(filepath)}")
    except Exception as e:
        print(f"✗ Error with {os.path.basename(filepath)}: {e}")

print("\n✓ All files processed!")
