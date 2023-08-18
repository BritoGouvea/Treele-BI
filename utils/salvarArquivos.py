import json

def salvar_json(dados, nome_arquivo):
    with open(nome_arquivo, 'w') as outfile:
        json.dump(dados, outfile, ensure_ascii=False, indent=4)