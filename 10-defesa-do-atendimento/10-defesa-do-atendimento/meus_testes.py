"""Os seus testes da defesa. Rode:

    python3 meus_testes.py                       testa o atendimento.py
    python3 meus_testes.py uma_copia_quebrada.py testa uma cópia

O primeiro teste é um exemplo. Escreva os outros pelo exercício da aula.
"""
import sys

from pagamentos import PagamentosFora  # noqa: F401  (você vai usar no teste da falha)
from testes import Conversa, pausou, rodar_testes


def teste_exemplo_financeiro_nega(m):
    """Exemplo: pedido 7, o financeiro responde False, nada sai."""
    c = Conversa(m, 'Cliente 0143')
    assert pausou(c.enviar('Quero o reembolso do pedido 7'))
    final = c.financeiro(False)
    assert final['atendido_por'] == 'negar', final.get('atendido_por')
    assert c.pagamentos.chamadas == 0, c.pagamentos.chamadas


TESTES = [teste_exemplo_financeiro_nega]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'atendimento.py'))
