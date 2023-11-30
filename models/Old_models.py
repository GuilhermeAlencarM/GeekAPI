from pydantic import BaseModel
from typing import Optional

class Produto(BaseModel):
  id: Optional[int] = None
  nome: str
  preco: float

class Camisa(Produto):
  tamanho: str
  
class Caneca(Produto):
  capacidade: str
  
class Quadrinho(Produto):
  autor: str
  editora: str
  