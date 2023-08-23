class Orçamento:

    def __init__(self, orçamento) -> None:
        self.planilhas = orçamento['planilhas']

class Planilha:

    def __init__(self, planilha: dict) -> None:
        self.id = planilha['id']
        self.descrição = planilha['descrição']
        self.status = planilha['status']
        self.itens = []

class Itens_Planilha:

    def __init__(self, item) -> None:
        self.id = item['id']
        self.wbs = item['wbs']