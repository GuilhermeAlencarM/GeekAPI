import random
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.produto_model import ProdutoModel, ProdutoResponse
from core.deps import get_session
from operator import attrgetter

router = APIRouter()


@router.get("/carrinho", response_model=List[ProdutoResponse], tags=["Sistema"])
async def listar_produtos(session: AsyncSession = Depends(get_session)):
    produtos = await session.execute(select(ProdutoModel))

    return produtos.scalars().all()


@router.get("/carrinho/{produto_id}", response_model=ProdutoResponse, tags=["Sistema"])
async def listar_produto(produto_id: int, session: AsyncSession = Depends(get_session)):
    produto = await session.get(ProdutoModel, produto_id)
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado.")
    return produto


@router.post("/carrinho", response_model=ProdutoResponse, tags=["Sistema"], status_code=status.HTTP_201_CREATED)
async def criar_produto(produto: ProdutoModel, session: AsyncSession = Depends(get_session)):
    produto_dict = produto.dict()
    produto_cleaned = ProdutoModel(**produto_dict)

    session.add(produto_cleaned)
    await session.commit()
    await session.refresh(produto_cleaned)
    return produto_cleaned


@router.delete("/carrinho/{produto_id}", tags=["Sistema"])
async def deletar_produto(produto_id: int, session: AsyncSession = Depends(get_session)):
    produto = await session.get(ProdutoModel, produto_id)
    await session.delete(produto)
    await session.commit()

    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Produto não encontrado.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def gerar_numero_serie(produto: ProdutoModel) -> Union[int, None]:
    if produto.tipo == "Camisa":
        return random.choice(range(0, 1001, 5))  # Múltiplos de 5 até 1000
    elif produto.tipo == "Caneca":
        return random.choice(range(0, 1001, 3))  # Múltiplos de 3 até 1000
    elif produto.tipo == "Quadrinho":
        return random.choice(range(0, 1001, 7))  # Múltiplos de 7 até 1000
    else:
        return None  # Tipo de produto desconhecido


@router.post("/finalizar-compra", tags=["Sistema"])
async def finalizar_compra(session: AsyncSession = Depends(get_session)):
    produtos = await session.execute(select(ProdutoModel))
    carrinho_ordenado = sorted(
        produtos.scalars().all(), key=attrgetter('preco'))

    # Aplicar promoção: 4 camisas = 1 caneca grátis
    qtd_camisas = sum(
        1 for produto in carrinho_ordenado if produto.tipo == "Camisa")
    qtd_canecas = sum(
        1 for produto in carrinho_ordenado if produto.tipo == "Caneca")
    if qtd_camisas >= 4 and qtd_canecas < 1:
        carrinho_ordenado.append(ProdutoModel(id=random.choice(range(
            0, 1001, 3)), nome="Caneca Brinde", tipo="Caneca", preco=0, capacidade="300ml"))

    # Aplicar promoção: 5 quadrinhos = menor valor grátis
    qtd_quadrinhos = sum(
        1 for produto in carrinho_ordenado if produto.tipo == "Quadrinho")
    if qtd_quadrinhos >= 5:
        precos_quadrinhos = [
            produto.preco for produto in carrinho_ordenado if produto.tipo == "Quadrinho"]
        # Ordena os preços dos quadrinhos do mais barato para o mais caro
        precos_quadrinhos.sort()
        for produto in carrinho_ordenado:
            if produto.tipo == "Quadrinho" and produto.preco == precos_quadrinhos[0]:
                produto.preco = 0
                break  # Apenas um quadrinho é grátis

    total = sum(produto.preco for produto in carrinho_ordenado)

    resposta = {
        "msg": "Compra finalizada com sucesso!",
        "Carrinho": [{
            "item": produto.dict(),
            "numero_serie": gerar_numero_serie(produto)
        } for produto in carrinho_ordenado],
        "Valor total": total,
    }

    return resposta
