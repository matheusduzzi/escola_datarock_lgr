"""O que o LangGraph guarda do pedido 4: a foto atual, o histórico de fotos e a trilha do servidor.

    python3 fotos.py                       com servidor.py
    python3 fotos.py versao_do_colega.py   com a versão do colega

Reproduz o pedido 4 de terça (o pedido e o retomar da noite, as duas tentativas recusadas) e
mostra o get_state e o get_state_history do thread. No fim, o que a trilha do servidor tem.
"""
import sys

from testes import SEM_COBRANCA, Operadora, carregar, passagens

s = carregar(sys.argv[1] if len(sys.argv) > 1 else 'servidor.py')
at = s.Atendimento(s.Banco(), Operadora())
try:
    at.pedir_reembolso(SEM_COBRANCA, 4)
except Exception:
    pass
t = next(iter(at.banco.donos))
try:
    at.retomar(t)
except Exception:
    pass

foto = at.grafo.get_state(s.config(t))
print('1. get_state do pedido 4')
print(f'   next: {foto.next}')
print(f'   erro guardado: {foto.tasks[0].error}')
print('2. get_state_history, da foto mais nova para a mais velha')
for f in at.grafo.get_state_history(s.config(t)):
    erros = [x.error for x in f.tasks if x.error]
    print(f"   passo {f.metadata['step']:>2}  next {f.next}" + (f'  erro {erros[0]}' if erros else ''))
trilha = at.trilha_de(t)
terminaram = [e['onde'] for e in passagens(trilha, evento='terminou')]
print(f"3. a trilha do servidor: {len(passagens(trilha, 'reembolsar', 'caiu'))} quedas do reembolsar; "
      f"nós que terminaram: {', '.join(terminaram) or 'nenhum'}")
