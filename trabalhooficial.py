from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class QuartoNaoAssociadoError(Exception):
    pass

class DiasInvalidosError(Exception):
    pass

class TipoDeQuarto(ABC):
    
    def __init__(self, nome: str, tarifa_diaria_base: float, taxa_servico_base: float):
        self._nome = nome
        self._tarifa_diaria_base = tarifa_diaria_base
        self._taxa_servico_base = taxa_servico_base

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def tarifa_diaria_base(self) -> float:
        return self._tarifa_diaria_base

    @property
    def taxa_servico_base(self) -> float:
        return self._taxa_servico_base

    @abstractmethod
    def calcular_valor_reserva(self, dias: int, consumo_minibar: float, taxa_ocupacao: float) -> float:
        pass

class QuartoStandard(TipoDeQuarto):

    def __init__(self, tarifa_diaria_base: float, taxa_servico_base: float, taxa_limpeza_adicional: float):
        super().__init__("Standard", tarifa_diaria_base, taxa_servico_base)
        self._taxa_limpeza_adicional = taxa_limpeza_adicional

    def calcular_valor_reserva(self, dias: int, consumo_minibar: float, taxa_ocupacao: float) -> float:
        valor_base = (self._tarifa_diaria_base * dias) * taxa_ocupacao
        
        valor_com_minibar = valor_base + consumo_minibar
        
        valor_com_taxa = valor_com_minibar * (1 + self._taxa_servico_base)
        
        if dias > 5:
            valor_final = valor_com_taxa + self._taxa_limpeza_adicional
        else:
            valor_final = valor_com_taxa
            
        return valor_final

class SuiteMaster(TipoDeQuarto):
 
    def __init__(self, tarifa_diaria_base: float, taxa_servico_base: float, desconto_fidelidade: float):
        super().__init__("Luxo", tarifa_diaria_base, taxa_servico_base)
        self._desconto_fidelidade = desconto_fidelidade

    def calcular_valor_reserva(self, dias: int, consumo_minibar: float, taxa_ocupacao: float) -> float:
        valor_base = (self._tarifa_diaria_base * dias) * taxa_ocupacao
        
        acrescimo_20 = valor_base * 0.20
        valor_com_acrescimo = valor_base + acrescimo_20
        
        valor_com_minibar = valor_com_acrescimo + consumo_minibar
        
        valor_com_taxa = valor_com_minibar * (1 + self._taxa_servico_base)

        if dias > 3:
            valor_final = valor_com_taxa - self._desconto_fidelidade
        else:
            valor_final = valor_com_taxa
            
        return valor_final

class UnidadeHospedagem:
    def __init__(self, numero_quarto: int, localizacao: str):
        self._numero_quarto = numero_quarto
        self._localizacao = localizacao
        self._tipo_quarto_associado: Optional[TipoDeQuarto] = None

    @property
    def numero_quarto(self) -> int:
        return self._numero_quarto

    @property
    def localizacao(self) -> str:
        return self._localizacao

    @property
    def tipo_quarto(self) -> Optional[TipoDeQuarto]:
        return self._tipo_quarto_associado

    def associar_tipo_quarto(self, tipo: TipoDeQuarto):
        self._tipo_quarto_associado = tipo

    def iniciar_reserva(self, dias: int, consumo_minibar: float, taxa_ocupacao: float) -> float:
    
        if self._tipo_quarto_associado is None:
            raise QuartoNaoAssociadoError(f"A Unidade {self._numero_quarto} não tem um TipoDeQuarto associado.")
        
        if dias <= 0:
            raise DiasInvalidosError("O número de dias da reserva deve ser positivo.")

        valor_total = self._tipo_quarto_associado.calcular_valor_reserva(
            dias, consumo_minibar, taxa_ocupacao
        )
        return valor_total

class Reserva:
    def __init__(self, unidade_reservada: UnidadeHospedagem, dias: int, consumo_minibar: float, taxa_ocupacao: float, valor_total_reserva: float):
        self._unidade_reservada = unidade_reservada
        self._dias = dias
        self._consumo_minibar = consumo_minibar
        self._taxa_ocupacao = taxa_ocupacao
        self._valor_total_reserva = valor_total_reserva 

    @property
    def unidade(self) -> UnidadeHospedagem:
        return self._unidade_reservada

    @property
    def valor_total(self) -> float:
        return self._valor_total_reserva

    def registrar_reserva(self, sistema_gerenciamento):
        sistema_gerenciamento._historico_reservas.append(self)

    def exibir_resumo(self):
        tipo_quarto = self._unidade_reservada.tipo_quarto.nome if self._unidade_reservada.tipo_quarto else "N/A"
        
        print("\n--- Detalhes da Transação (Reserva) ---")
        print(f"Quarto: {self._unidade_reservada.numero_quarto} ({tipo_quarto})")
        print(f"Localização: {self._unidade_reservada.localizacao}")
        print(f"Dias de Estadia: {self._dias}")
        print(f"Consumo Minibar: R$ {self._consumo_minibar:.2f}")
        print(f"Valor Total da Reserva: R$ {self._valor_total_reserva:.2f}")
        print("--------------------------------------")

class SistemaDeGerenciamentoDeHospedagem:
    def __init__(self):
        self._quartos: List[UnidadeHospedagem] = [] 
        self._historico_reservas: List[Reserva] = []

    def adicionar_quarto(self, quarto: UnidadeHospedagem):
        self._quartos.append(quarto)

    def listar_quartos(self):
        print("\n--- Quartos Registrados ---")
        for quarto in self._quartos:
            tipo = quarto.tipo_quarto.nome if quarto.tipo_quarto else "NÃO ASSOCIADO"
            tarifa = quarto.tipo_quarto.tarifa_diaria_base if quarto.tipo_quarto else 0.0
            print(f"Quarto {quarto.numero_quarto} ({quarto.localizacao}) - Tipo: {tipo} (Tarifa Base: R$ {tarifa:.2f})")
        print("---------------------------")

    def registrar_reserva(self, numero_quarto: int, dias: int, consumo_minibar: float, taxa_ocupacao: float):
        quarto_selecionado = next((q for q in self._quartos if q.numero_quarto == numero_quarto), None)
        
        if quarto_selecionado is None:
            print(f"Erro: Quarto número {numero_quarto} não encontrado.")
            return

        try:
            valor_total = quarto_selecionado.iniciar_reserva(dias, consumo_minibar, taxa_ocupacao)
            
            nova_reserva = Reserva(quarto_selecionado, dias, consumo_minibar, taxa_ocupacao, valor_total)
            
            nova_reserva.registrar_reserva(self)
            
            print(f"\nSucesso: Reserva para o Quarto {numero_quarto} registrada.")
            nova_reserva.exibir_resumo()
            
        except (QuartoNaoAssociadoError, DiasInvalidosError) as e:
            print(f"\nFalha ao registrar reserva: {e}")
        except Exception as e:
            print(f"\nErro inesperado: {e}")

    def resumo_faturamento_mensal(self):
        total_faturado = sum(reserva.valor_total for reserva in self._historico_reservas)
        print("\n--- Resumo de Faturamento ---")
        print(f"Total de Reservas Registradas: {len(self._historico_reservas)}")
        print(f"Faturamento Total: R$ {total_faturado:.2f}")
        print("-----------------------------")

def demonstracao():
    sistema = SistemaDeGerenciamentoDeHospedagem()

    standard_type = QuartoStandard(
        tarifa_diaria_base=150.00, 
        taxa_servico_base=0.10, 
        taxa_limpeza_adicional=50.00 
    )
    master_type = SuiteMaster(
        tarifa_diaria_base=300.00, 
        taxa_servico_base=0.15,
        desconto_fidelidade=30.00 
    )

    q101 = UnidadeHospedagem(101, "1º andar, vista mar")
    q102 = UnidadeHospedagem(102, "1º andar, vista interna")
    q201 = UnidadeHospedagem(201, "2º andar, vista mar")

    q101.associar_tipo_quarto(standard_type)
    q102.associar_tipo_quarto(standard_type)
    q201.associar_tipo_quarto(master_type)

    sistema.adicionar_quarto(q101)
    sistema.adicionar_quarto(q102)
    sistema.adicionar_quarto(q201)
    
    q301 = UnidadeHospedagem(301, "3º andar, cobertura")
    sistema.adicionar_quarto(q301)

    sistema.listar_quartos()

    print("\n--- Teste de Reservas ---")
    sistema.registrar_reserva(101, dias=3, consumo_minibar=20.00, taxa_ocupacao=1.0) 

    sistema.registrar_reserva(102, dias=7, consumo_minibar=0.00, taxa_ocupacao=1.0) 
    sistema.registrar_reserva(201, dias=4, consumo_minibar=50.00, taxa_ocupacao=1.0) 

    print("\n--- Teste de Exceções ---")
    sistema.registrar_reserva(301, dias=2, consumo_minibar=10.00, taxa_ocupacao=1.0)
    sistema.registrar_reserva(101, dias=0, consumo_minibar=10.00, taxa_ocupacao=1.0)

    sistema.resumo_faturamento_mensal()

if __name__ == "__main__":
    demonstracao()
