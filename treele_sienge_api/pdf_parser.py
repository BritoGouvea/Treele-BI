import pdfplumber

def row_to_dict(row):
    return {
        "Insumo": row[0],
        "Obra": row[1],
        "Data": row[2],
        "Solicitante": row[3],
        "Solicitação": row[4],
        "Autorizado": row[5],
        "Data da autorização": row[6],
        "Atendimentos": [{
            "Quantidade pendente": row[7],
            "Unidade": row[8],
            "Quantidade atendida": row[9],
            "Sd.": row[10],
            "Data previsão": row[11],
            "Data atendida": row[12],
            "Diferença": row[13]
        }]
    }

tables = []

with pdfplumber.open('../assets/relatorio.pdf') as pdf:
    for page in pdf.pages:
        tables.extend(page.extract_tables())

insumos = []
for table in tables:
    if table[0][0] == '':
        continue
    for i, row in enumerate(table):
        if row[0] != 'Insumo':
            if row[0] != None:
                insumos.append(row_to_dict(row))
            else:
                noneRow = row_to_dict(row)
                insumos[-1]["Atendimentos"].append(noneRow["Atendimentos"][0])

for insumo in insumos:
    insumo['Insumo'] = insumo['Insumo'].replace('\n', ' ')
    try:
        insumo['Solicitante'] = insumo['Solicitante'].replace('\n', '')
    except:
        pass

import json
from datetime import datetime

date_format = '%d/%m/%Y'

insumos = json.load(open("../assets/RequestsRelations.json"))

for insumo in insumos:
    try:
        insumo['Data'] = datetime.strptime(insumo['Data'], date_format).isoformat()
        insumo['Data da autorização'] = datetime.strptime(insumo['Data da autorização'], date_format).isoformat()
    except:
        pass
    try:
        insumo['Solicitação'] = int(insumo['Solicitação'])
    except:
        pass
    
with open("RequestsRelations.json", "w") as outfile:
    json.dump(insumos, outfile, ensure_ascii=False, indent=4)
