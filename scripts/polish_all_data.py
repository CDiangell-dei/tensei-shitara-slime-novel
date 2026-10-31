import os
import glob
from fix_translation import fix_file

def polish_all():
    print("Iniciando polimento e padronização de todos os volumes da Light Novel...")
    ln_files = glob.glob('data/light_novel/*.json')
    for f in ln_files:
        fix_file(f, f)
        
    print("\nIniciando polimento de todos os capítulos da Web Novel...")
    wn_files = glob.glob('data/web_novel/*.json')
    for f in wn_files:
        fix_file(f, f)
        
    print("\nTodos os arquivos foram polidos e padronizados com sucesso!")

if __name__ == '__main__':
    polish_all()
