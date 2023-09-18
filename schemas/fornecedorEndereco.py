from unicodedata import category
from pydantic import BaseModel, Field
from typing import Optional, List

class FornecedorEnderecoSchema(BaseModel):
    fornecedorEndereco_id:  int = Field(..., description="ID do fornecedor associado")
    cep:                    str = Field('12237-865')
    tipo_endereco:          str = Field('Faturamento')
    endereco:               str = Field('Rua das Araras, 122')
    cidade:                 str = Field('São Paulo')
    uf:                     str = Field('SP')

class FornecedorEnderecoPUTSchema(BaseModel):
    fornecedor_id: int = 0
    id:            int = 0
    cep:           str = Field('12237-865')
    tipo_endereco: str = Field('Faturamento')
    endereco:      str = Field('Rua das Araras, 122')
    cidade:        str = Field('São Paulo')
    uf:            str = Field('SP')


class FornecedorEnderecoBuscaSchema(BaseModel):
    id: Optional[int] = Field(1)
    tipo_endereco: Optional[str] = Field("Faturamento")

class FornecedorEnderecoDeleteSchema(BaseModel):
    id_end: int = 1
    fornecedor_id: int = 1

class FornecedorEnderecoDelSchema(BaseModel):
    mesage: str
    id: int

def apresenta_fornecedor_endereco(endereco_fornecedor):
    uf = 'SP'

    return {
        "id": endereco_fornecedor.id,
        "fornecedor_id": endereco_fornecedor.fornecedor_id,
        "cep": endereco_fornecedor.cep,
        "tipo_endereco": endereco_fornecedor.tipo_endereco,
        "endereco": endereco_fornecedor.endereco,
        "cidade": endereco_fornecedor.cidade,
        "uf": uf,
    }

class FornecedorEnderecoViewSchema(BaseModel):
    fornecedor_id: int = 1
    id: int = 1

class FornecedorIdEnderecoViewSchema(BaseModel):
    fornecedor_id: int = 1


class FornecedorEnderecoListaViewSchema(BaseModel):
    fornecedores: List[FornecedorEnderecoViewSchema]


def apresenta_lista_fornecedor_endereco(fornecedor_enderecos):
    result = []
    for fornecedor_endereco in fornecedor_enderecos:
        result.append(apresenta_fornecedor_endereco(fornecedor_endereco))
    return {"enderecos_fornecedores": result}

class FornecedorEnderecoDelSchema(BaseModel):
    mesage: str
    id: int

def apresenta_fornecedor_endereco(fornecedor_endereco):
     
    return {
        "id": fornecedor_endereco.id,
        "fornecedor_id": fornecedor_endereco.fornecedor_id,
        "cep": fornecedor_endereco.cep,
        "tipo_endereco": fornecedor_endereco.tipo_endereco,
        "endereco": fornecedor_endereco.endereco,
        "cidade": fornecedor_endereco.cidade,
        "uf": fornecedor_endereco.uf,
    }