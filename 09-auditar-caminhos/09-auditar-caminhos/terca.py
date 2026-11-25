"""A noite de terça reproduzida contra um servidor e comparada com a trilha exportada.

    python3 terca.py                         com servidor.py e o retomar da noite de terça
    python3 terca.py versao_do_colega.py     com a versão do colega
    python3 terca.py servidor.py conserto    a mesma noite com o retomar_parados

As mesmas entradas, na mesma ordem: a Cliente 0112 pede o reembolso do pedido 4, a operadora
cai, a Cliente 0143 pede o do pedido 101, e às 2h roda o retomar da noite. A hora e o código dos
threads ficam de fora da comparação.
"""
import sys

from testes import (EXTRATO_TERCA, LUMINARIA, SEM_COBRANCA, TERCA, Operadora, carregar, comparar, extrato,
                    ler_extrato, ler_trilha, por_pedido, trilha_toda)


def noite_de_terca(at):
    """O retomar que rodava às 2h na terça, copiado do historia.py da aula 08."""
    for t in at.parados():
        at.retomar(t)


def reproduzir(m, conserto=False):
    banco, op = m.Banco(), Operadora()
    at = m.Atendimento(banco, op)
    try:
        at.pedir_reembolso(SEM_COBRANCA, 4)
        print(f'   {SEM_COBRANCA} pede o reembolso do pedido 4: respondeu')
    except Exception as erro:
        print(f'   {SEM_COBRANCA} pede o reembolso do pedido 4: a tela dela recebeu um erro ({type(erro).__name__})')
    op.cair('antes')
    _, resposta = at.pedir_reembolso(LUMINARIA, 101)
    print(f'   a operadora cai; {LUMINARIA} pede o do pedido 101: {resposta}')
    try:
        at.retomar_parados() if conserto else noite_de_terca(at)
        print('   o retomar da noite: terminou')
    except Exception as erro:
        print(f'   o retomar da noite: parou com {type(erro).__name__}')
    if hasattr(at, 'incompletos'):
        for i in at.incompletos():
            print(f"   de manhã, pedido {i['pedido']}: parado em {i['onde']}; {i['motivo']}")
    else:
        parados = [str(at.grafo.get_state(m.config(t)).values['id_pedido']) for t in at.parados()]
        print(f"   de manhã, parados: {', '.join('pedido ' + p for p in parados) or 'nenhum'}")
    print(f"   estornos na operadora: {', '.join(f'{p} ({m.reais(float(v))})' for p, v in extrato(op)) or 'nenhum'}")
    return trilha_toda(at), op


if __name__ == '__main__':
    arquivo = sys.argv[1] if len(sys.argv) > 1 else 'servidor.py'
    conserto = 'conserto' in sys.argv[2:]
    m = carregar(arquivo)
    print(f"1. A noite de terça com {arquivo}{', com o retomar_parados' if conserto else ''}")
    trilha, op = reproduzir(m, conserto)
    print('2. Comparação com exportado/trilha-de-terca.jsonl')
    exportada = ler_trilha(TERCA)
    feitos = por_pedido(trilha)
    for pedido, passos in por_pedido(exportada).items():
        iguais = sum(1 for a, b in zip(feitos.get(pedido, []), passos) if a == b)
        print(f'   pedido {pedido}: {len(feitos.get(pedido, []))} aqui, {len(passos)} na exportada, {iguais} iguais na ordem')
    diferencas = comparar(trilha, exportada)
    for d in diferencas:
        print(f'   {d}')
    extrato_igual = extrato(op) == ler_extrato(EXTRATO_TERCA)
    print(f"   extrato da operadora: {'igual' if extrato_igual else 'diferente'}")
    bate = not diferencas and extrato_igual
    print('   a reprodução bate com a noite de terça' if bate else '   a reprodução não bate com a noite de terça')
