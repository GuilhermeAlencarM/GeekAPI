from pydantic import BaseModel, validator
from typing import Optional
from sqlmodel import SQLModel, Field


class ProdutoModel(SQLModel, table=True):
    __tablename__: str = "produtos"

    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str
    nome: str
    preco: float
    tamanho: Optional[str] = None
    capacidade: Optional[str] = None
    autor: Optional[str] = None
    editora: Optional[str] = None

    @validator("preco")
    def validar_preco(cls, preco):
        if preco < 0:
            raise ValueError("Preço não pode ser negativo.")
        return preco


class ProdutoResponse(BaseModel):
    id: int
    tipo: str
    nome: str
    preco: float
    tamanho: Optional[str] = None
    capacidade: Optional[str] = None
    autor: Optional[str] = None
    editora: Optional[str] = None

    class Config:
        orm_mode = True
