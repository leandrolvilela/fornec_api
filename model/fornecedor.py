from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base

class Fornecedor(Base):
    __tablename__ = 'fornecedor'

    id = Column("id", Integer, primary_key=True)
    nome = Column(String(140), unique=True)
    descricao = Column(String(4000))
    categoria = Column(String(200))
    data_insercao = Column(DateTime, default=datetime.now())
    enderecos = relationship("FornecedorEndereco", back_populates="fornecedor")

    def __init__(self, nome:str, descricao:str, categoria:str, data_insercao:Union[DateTime, None] = None):
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        if data_insercao:
            self.data_insercao = data_insercao
