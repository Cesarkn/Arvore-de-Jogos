from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


class NoJogo:
    def __init__(self, tabuleiro, tipo):
        self.tabuleiro = tabuleiro
        self.tipo = tipo
        self.filhos = []


def expand(no):
    filhos = []
    for i in range(3):
        for j in range(3):
            if no.tabuleiro[i][j] == ' ':
                novo_tabuleiro = [linha[:] for linha in no.tabuleiro]
                novo_tabuleiro[i][j] = 'x' if no.tipo == '+' else 'o'
                novo_tipo = '-' if no.tipo == '+' else '+'
                filho = NoJogo(novo_tabuleiro, novo_tipo)
                filhos.append(filho)
    return filhos


def verificar_vitoria(tabuleiro):
    for i in range(3):
        if tabuleiro[i][0] == tabuleiro[i][1] == tabuleiro[i][2] != ' ':
            return tabuleiro[i][0]
        if tabuleiro[0][i] == tabuleiro[1][i] == tabuleiro[2][i] != ' ':
            return tabuleiro[0][i]

    if tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] != ' ':
        return tabuleiro[0][0]
    if tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] != ' ':
        return tabuleiro[0][2]

    return None


def calcular_qualidade(tabuleiro):
    def contar_livres(simbolo):
        livre = 0
        for i in range(3):
            if all(tabuleiro[i][j] in [simbolo, ' '] for j in range(3)):
                livre += 1
        for j in range(3):
            if all(tabuleiro[i][j] in [simbolo, ' '] for i in range(3)):
                livre += 1
        if all(tabuleiro[i][i] in [simbolo, ' '] for i in range(3)):
            livre += 1
        if all(tabuleiro[i][2 - i] in [simbolo, ' '] for i in range(3)):
            livre += 1
        return livre

    vitoria = verificar_vitoria(tabuleiro)
    if vitoria == 'x':
        return 9
    elif vitoria == 'o':
        return -9

    livres_x = contar_livres('x')
    livres_o = contar_livres('o')

    return livres_x - livres_o


def buildTree(tabuleiro, profundidade):
    raiz = NoJogo(tabuleiro, '+')
    if profundidade == 0 or verificar_vitoria(tabuleiro):
        return raiz
    raiz.filhos = expand(raiz)
    for filho in raiz.filhos:
        filho.filhos = buildTree(filho.tabuleiro, profundidade - 1).filhos
    return raiz


def bestBranch(no):
    if not no.filhos:
        return calcular_qualidade(no.tabuleiro)

    if no.tipo == '+':
        return max(bestBranch(filho) for filho in no.filhos)
    else:
        return min(bestBranch(filho) for filho in no.filhos)


@app.route('/melhor-jogada', methods=['POST'])
def melhor_jogada():
    data = request.json
    tabuleiro = data['tabuleiro']
    profundidade = data.get('profundidade', 9)

    arvore_jogo = buildTree(tabuleiro, profundidade)
    melhor_jogada = bestBranch(arvore_jogo)
    return jsonify({'melhor_jogada': melhor_jogada})


if __name__ == '__main__':
    app.run(debug=True)
