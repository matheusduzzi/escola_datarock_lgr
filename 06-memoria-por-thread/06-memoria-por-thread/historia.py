"""As duas reclamações da coordenadora, rodadas contra um servidor.

    python3 historia.py                       com servidor.py
    python3 historia.py versao_do_colega.py   com a versão do colega
"""
import sys

from testes import DELA, DELE, RECUSA, carregar, contar_fotos


def falar(quem, texto, resposta):
    print(f'   {quem}: {texto}')
    print(f'   atendimento: {resposta}')


def reinicio(m):
    print('1. A conversa nova depois do reinício')
    banco = m.Banco()
    antes = m.Atendimento(banco)
    dela = antes.nova_conversa(DELA)
    texto = 'Quero saber do pedido 7'
    falar(DELA, texto, antes.enviar(dela, DELA, texto))
    depois = m.Atendimento(banco)  # o processo novo; o banco continua igual
    print('   o servidor reinicia; o banco continua com as conversas')
    dele = depois.nova_conversa(DELE)
    print(f"   o código da conversa nova do {DELE} é o mesmo da conversa da {DELA}? "
          f"{'sim' if dele == dela else 'não'}")
    texto = 'Qual o valor do meu último pedido?'
    falar(DELE, texto, depois.enviar(dele, DELE, texto))
    print(f'   dono da conversa da {DELA} no banco: {banco.donos.get(dela)}')


def reenvio(m):
    print('2. O app reenvia a mensagem depois de perder a conexão')
    at = m.Atendimento(m.Banco())
    dela = at.nova_conversa(DELA)
    texto = 'Quero saber do pedido 7'
    falar(DELA, texto, at.enviar(dela, DELA, texto))
    fotos = contar_fotos(at, dela)
    print(f'   o {DELE} abre o link da conversa da {DELA}')
    if not at.abrir(dela, DELE):
        print(f'   porta: {RECUSA}')
    print('   o app perde a conexão e reenvia a mensagem com o código do link')
    texto = 'Qual o valor do meu último pedido?'
    falar(DELE, texto, at.enviar(dela, DELE, texto))
    print(f'   fotos da conversa da {DELA}: {fotos} antes, {contar_fotos(at, dela)} depois')


if __name__ == '__main__':
    m = carregar(sys.argv[1] if len(sys.argv) > 1 else 'servidor.py')
    reinicio(m)
    reenvio(m)
