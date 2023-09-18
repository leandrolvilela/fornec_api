from unicodedata import category
from pydantic import BaseModel
from typing import Optional, List

class FornecedorSchema(BaseModel):
    nome:       str = "Microsot"
    descricao:  str = "Microsoft"
    categoria:  str = "Fabricante"

class FornecedorBuscaSchema(BaseModel):
    id: Optional[int] = 1
    nome: Optional[str] = "Microsoft"

def apresenta_fornecedor(fornecedor):
    return {
        "id": fornecedor.id,
        "nome": fornecedor.nome,
        "descricao": fornecedor.descricao,
        "categoria": fornecedor.categoria,
    }

class FornecedorViewSchema(BaseModel):
    id: int = 1
    nome: str = "Microsot"
    descricao: Optional[str] = "Fabricante Pacote Office "
    categoria: str = "Fabricante"


class FornecedorListaViewSchema(BaseModel):
    fornecedores: List[FornecedorViewSchema]


def apresenta_lista_fornecedor(fornecedores):
    result = []
    for fornecedor in fornecedores:
        result.append(apresenta_fornecedor(fornecedor))
    return {"fornecedores": result}

class FornecedorDelSchema(BaseModel):
    mesage: str
    id: int

def apresenta_fornecedor(fornecedor):
     
    return {
        "id": fornecedor.id,
        "nome": fornecedor.nome,
        "categoria": fornecedor.categoria,
        "descricao": fornecedor.descricao,
    }
