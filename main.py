from fastapi import status
from fastapi import FastAPI, HTTPException
from models import Camisa, Caneca, Quadrinho
from typing import Union

app = FastAPI()

carrinho = []
camisas_compradas = 0
quadrinhos_comprados = 0
produtos_promocionais = []


@app.get('/carrinho')
async def ver_carrinho():
    return carrinho, produtos_promocionais

@app.get('/carrinho/{id}')
async def ver_item_do_carrinho(id: int):
    modified_id = id - 1
    try:
        item = carrinho[modified_id]
        return item
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não cadastrado.")


@app.post('/carrinho', status_code=status.HTTP_201_CREATED)
async def adicionar_produto_ao_carrinho(produto: Union[Camisa, Caneca, Quadrinho]):
    global camisas_compradas, quadrinhos_comprados
    produto.id = len(carrinho) + 1
    carrinho.append(produto)

    if isinstance(produto, Camisa):
        camisas_compradas += 1
        if camisas_compradas % 4 == 0:
            produtos_promocionais.append(
                Caneca(nome="Caneca de brinde", preco=0, capacidade="300ml"))
            camisas_compradas = 0
    elif isinstance(produto, Quadrinho):
        quadrinhos_comprados += 1
        if quadrinhos_comprados % 5 == 0:
            menor_preco_quadrinho = min(
                [produto for produto in carrinho if isinstance(produto, Quadrinho)], key=lambda q: q.preco)
            menor_preco_quadrinho.preco = 0

    return produto


@app.delete('/carrinho/{id}')
async def remover_produto_do_carrinho(id: int):
    modified_id = id - 1
    try:
        if carrinho[modified_id] in carrinho:
            del carrinho[modified_id]
            return {'msg': 'Produto excluído com sucesso!'}
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não cadastrado.")


@app.post('/finalizar_compra')
async def finalizar_compra():
    total = sum(produto.preco for produto in carrinho)
    resposta = {
        "msg": "Compra finalizada com sucesso!",
        "carrinho": [produto.dict() for produto in carrinho],
        "promocao": [produto.dict() for produto in produtos_promocionais],
        "total": total,
    }

    return resposta


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='127.0.0.1', port=8000,
                log_level='info', reload=True)