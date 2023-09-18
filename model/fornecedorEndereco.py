from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base

class FornecedorEndereco(Base):
    __tablename__ = 'fornecedor_endereco'

    id              = Column("id", Integer, primary_key=True)
    fornecedor_id   = Column(Integer, ForeignKey('fornecedor.id'), nullable=False)
    cep             = Column(String(10), nullable=False)
    tipo_endereco   = Column(String(50), nullable=False)
    endereco        = Column(String(4000))
    cidade          = Column(String(200))
    uf              = Column(String(2))
    data_insercao   = Column(DateTime, default=datetime.now())
    fornecedor      = relationship("Fornecedor", back_populates="enderecos")

    def __init__(self,fornecedor_id: int, cep:str, tipo_endereco:str, endereco:str, cidade:str, uf:str, data_insercao:Union[DateTime, None] = None):
        self.fornecedor_id  = fornecedor_id
        self.cep            = cep
        self.tipo_endereco  = tipo_endereco
        self.endereco       = endereco
        self.cidade         = cidade
        self.uf             = uf
        if data_insercao:
            self.data_insercao = data_insercao