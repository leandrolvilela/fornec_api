from email.mime import base
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI
from flask_cors import CORS
from flask import redirect, jsonify, request
from model import Session, Produto, Fornecedor, FornecedorEndereco
from logger import logger
from schemas import *


info = Info(title="Minha querida API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
produto_tag = Tag(name="Produto", description="Adição, visualização e remoção de produtos à base")
fornecedor_tag  = Tag(name="Fornecedor", description="Adição, visualização e remoção de fornecedores à base")
fornecedor_endereco_tag  = Tag(name="fornecedor_endereco", description="Adição, visualização e remoção de endereços à base")

@app.get('/')
def home():
    return redirect('/openapi')

# --------------------
#   FORNECEDOR
#---------------------

@app.post('/fornecedor', tags=[fornecedor_tag],
          responses={"200": FornecedorSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_fornecedor(form: FornecedorSchema):
    """Adiciona um novo Fornecedor à base de dados"""

    print(f'NOME: {form.nome} - {form.descricao} - {form.categoria}')
    
    fornecedor = Fornecedor(
        nome=form.nome,
        descricao=form.descricao,
        categoria=form.categoria
    )

    session = Session()
    logger.debug(f"Adicionando fornecedor de nome: '{fornecedor.nome}'")
    try:
        session.add(fornecedor)
        session.commit()
        logger.debug(f"Adicionado fornecedor de nome: '{fornecedor.nome}'")
        return apresenta_fornecedor(fornecedor), 200
    except IntegrityError as e:
        error_msg = "Fornecedor de mesmo nome já existe na base :/"
        logger.warning(f"Erro ao adicionar fornecedor '{fornecedor.nome}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar o novo fornecedor :/"
        logger.warning(f"Erro ao adicionar fornecedor '{fornecedor.nome}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/fornecedor', tags=[fornecedor_tag],
         responses={"200": FornecedorViewSchema, "404": ErrorSchema})
def get_fornecedor(query: FornecedorViewSchema):
    """Faz a busca por um fornecedor a partir do id do fornecedor

    Retorna uma representação dos fornecedors e comentários associados.
    """
    fornecedorEndereco_id = query.id
    logger.debug(f"Coletando dados sobre fornecedor #{fornecedorEndereco_id}")
    session = Session()
    fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedorEndereco_id).first()
    if not fornecedor:
        error_msg = "fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao buscar fornecedor '{fornecedorEndereco_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"fornecedor econtrado: '{fornecedor.nome}'")
        return apresenta_fornecedor(fornecedor), 200

@app.get('/fornecedores', tags=[fornecedor_tag],
         responses={"200": FornecedorListaViewSchema, "404": ErrorSchema})
def get_fornecedores():
    """Lista todos os fornecedores cadastrados na base

    Retorna uma lista de representações de fornecedores.
    """
    logger.debug(f"Coletando lista de fornecedores")
    session = Session()
    fornecedores = session.query(Fornecedor).all()
    
    # for fornecedor in fornecedores:
    #     print(f'LISTA FORNECEDOR: {fornecedor.id} - {fornecedor.nome} DESCRIÇÃO: {fornecedor.descricao}')
    
    if not fornecedores:
        error_msg = "fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao buscar por lista de fornecedores. {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"Retornando lista de fornecedores")
        return apresenta_lista_fornecedor(fornecedores), 200

@app.delete('/fornecedor', tags=[fornecedor_tag],
            responses={"200": FornecedorDelSchema, "404": ErrorSchema})
def del_fornecedor(query: FornecedorBuscaSchema):
    """Deleta um fornecedor a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    fornecedorEndereco_id = query.id
    fornecedor_nome = query.nome

    logger.debug(f"Deletando dados sobre fornecedor #{fornecedorEndereco_id}")
    session = Session()

    try:
        if fornecedorEndereco_id:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedorEndereco_id).one()
        else:
            fornecedor = session.query(Fornecedor).filter(Fornecedor.nome == fornecedor_nome).one()

        # Verifique se existem endereços associados ao fornecedor
        if fornecedor.enderecos:
            error_msg = "Não é possível excluir um fornecedor com endereços associados."
            logger.warning(f"Erro ao deletar fornecedor #{fornecedorEndereco_id}, {error_msg}")
            return {"message": error_msg}, 400

        if fornecedorEndereco_id:
            count = session.query(Fornecedor).filter(Fornecedor.id == fornecedorEndereco_id).delete()
        else:
            count = session.query(Fornecedor).filter(Fornecedor.nome == fornecedor_nome).delete()

        session.commit()
        if count:
            logger.debug(f"Deletado fornecedor #{fornecedorEndereco_id}")
            return {"mesage": "fornecedor removido", "id": fornecedorEndereco_id}
        else: 
            error_msg = "fornecedor não encontrado na base :/"
            logger.warning(f"Erro ao deletar fornecedor #'{fornecedorEndereco_id}', {error_msg}")
            return {"mesage": error_msg}, 400
        
    except NoResultFound:
        error_msg = "Fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao deletar fornecedor #{fornecedorEndereco_id}, {error_msg}")
        return {"message": error_msg}, 404  # Usamos 404 para indicar que o recurso não foi encontrado


@app.before_request
def before_request():
    if request.content_type == 'application/json':
        request.json_data = request.get_json()
        print(f"Entrou {request.json_data}")

@app.put('/fornecedor', tags=[fornecedor_tag],
         responses={"200": FornecedorViewSchema, "404" : ErrorSchema})
def upd_fornecedor(query: FornecedorViewSchema):
    """Atualiza uma Fornecedor a partir do ID da Fornecedor informado
    
    Retorna uma mensagem de confirmação da atualização
    """
    query = request.json_data

    print(f"ID: {query['id']} NOME: {query['nome']} DESCRIÇÃO: {query['descricao']} CATEGORIA: {query['categoria']}")

    fornecedor_id        = query['id']
    fornecedor_nome      = query['nome']
    fornecedor_descricao = query['descricao']
    fornecedor_categoria = query['categoria']

    logger.debug(f"Atualizando dados sobre a Fornecedor #{fornecedor_nome}")

    # Criando conexão com a base
    session = Session()
    
    try:
        # Fazendo a busca pelo ID da Fornecedor
        db_fornecedor = session.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
        
        if not db_fornecedor:
            # Se a Fornecedor não foi encontrado
            error_msg = f"Fornecedor não encontrada na base.\nDetalhe: {repr(e)}"
            logger.warning(f"Erro ao buscar a Fornecedor '{fornecedor_id}', {error_msg}")
            return {"message": error_msg}, 404
        else:


            db_fornecedor.nome      = fornecedor_nome
            db_fornecedor.descricao = fornecedor_descricao
            db_fornecedor.categoria = fornecedor_categoria
            # db_fornecedor.nome      = upd_campo_modificados(db_fornecedor.nome, fornecedor_nome)
            # db_fornecedor.decricao  = upd_campo_modificados(db_fornecedor.descricao, fornecedor_descricao)
            # db_fornecedor.categoria = upd_campo_modificados(db_fornecedor.categoria, fornecedor_categoria)

            # Grava alteração
            session.add(db_fornecedor)

            # Gravando a atualização
            session.commit()

            logger.debug(f"Editado Fornecedor de nome: '{db_fornecedor.nome}' - '{db_fornecedor.descricao}'")
            return apresenta_fornecedor(db_fornecedor), 200
        
    except IntegrityError as e:
        # Tratamento para erro de integridade do banco de dados
        error_msg = f"Fornecedor de mesmo nome já salvo na base :\n {repr(e)}"
        logger.error(f"Erro de integridade do banco de dados ao atualizar a Fornecedor: {error_msg}")
        return {"message": error_msg}, 500

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = f"Não foi possível salvar novo item.\nDetalhe: {repr(e)}"
        logger.warning(f"Erro ao adicionar Fornecedor '{db_fornecedor.nome}', {error_msg}")
        print(f"ERRO: {error_msg}")
        return {"message": error_msg}, 400

# ------------------------
#   ENDEREÇO FORNECEDOR
#-------------------------

@app.post('/fornecedor_endereco', tags=[fornecedor_endereco_tag],
          responses={"200": FornecedorEnderecoSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_fornecedor_endereco(form: FornecedorEnderecoSchema):
    """Adiciona um novo Endereço de Fornecedor à base de dados"""
    session = Session()
    endereco_fornecedor = FornecedorEndereco(
        fornecedor_id=form.fornecedorEndereco_id,
        cep=form.cep,
        tipo_endereco=form.tipo_endereco,
        endereco=form.endereco,
        cidade=form.cidade,
        uf=form.uf
        )
    logger.debug(f"Adicionando endereço de fornecedor com ID: '{endereco_fornecedor.fornecedor_id}'")
    try:
        session.add(endereco_fornecedor)
        session.commit()
        logger.debug(f"Adicionado endereço de fornecedor com ID: '{endereco_fornecedor.fornecedor_id}'")
        return apresenta_fornecedor_endereco(endereco_fornecedor), 200
    except IntegrityError as e:
        error_msg = "Endereço de fornecedor já existe :/"
        logger.warning(f"Erro ao adicionar endereço de fornecedor com ID: '{endereco_fornecedor.fornecedor_id}', {error_msg}")
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar o novo endereço de fornecedor :/"
        logger.warning(f"Erro ao adicionar endereço de fornecedor com ID: '{endereco_fornecedor.fornecedor_id}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/fornecedor_endereco', tags=[fornecedor_endereco_tag],
         responses={"200": FornecedorEnderecoViewSchema, "404": ErrorSchema})
def get_fornecedor_endereco(query: FornecedorEnderecoViewSchema):
    """Faz a busca por um endereço do fornecedor a partir do id do endereço

    Retorna uma representação dos endereços do fornecedor.
    """
    fornecedor_id = query.fornecedor_id
    logger.debug(f"Coletando dados sobre fornecedor #{fornecedor_id}")
    session = Session()
    # fornecedor_endereco = session.query(FornecedorEndereco).filter(FornecedorEndereco.id == fornecedorEndereco_id).first()
    fornecedor_endereco = session.query(FornecedorEndereco).filter(FornecedorEndereco.fornecedor_id == fornecedor_id).all()
    if not fornecedor_endereco:
        error_msg = "fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao buscar fornecedor '{fornecedor_id}', {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"fornecedor econtrado")
        return apresenta_lista_fornecedor_endereco(fornecedor_endereco), 200


@app.get('/fornecedor_enderecos', tags=[fornecedor_endereco_tag],
         responses={"200": FornecedorEnderecoListaViewSchema, "404": ErrorSchema})
def get_fornecedor_enderecos():
    """Lista todos os endereços dos fornecedores cadastrados na base

    Retorna uma lista de representações dos endereços do fornecedor.
    """
    logger.debug(f"Coletando lista de endereços do fornecedor")
    session = Session()
    fornecedor_enderecos = session.query(FornecedorEndereco).all()
    print(fornecedor_enderecos)
    if not fornecedor_enderecos:
        error_msg = "Endereço do fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao buscar por lista de endereços do fornecedor. {error_msg}")
        return {"mesage": error_msg}, 400
    else:
        logger.debug(f"Retornando lista de endereços do fornecedor")
        return apresenta_lista_fornecedor_endereco(fornecedor_enderecos), 200



@app.get('/fornecedor_enderecos_id', tags=[fornecedor_endereco_tag],
         responses={"200": FornecedorEnderecoListaViewSchema, "404": ErrorSchema})
def get_fornecedor_enderecos_id(query: FornecedorIdEnderecoViewSchema):
    """Lista todos os endereços do fornecedor informado cadastrados na base

    Retorna uma lista de representações dos endereços do fornecedor informado.
    """
    fornecedor_id = query.fornecedor_id
    
    logger.debug(f"Coletando lista de endereços do fornecedor")
    session = Session()

    try:
        fornecedor = session.query(Fornecedor).filter_by(id=fornecedor_id).first()
        if not fornecedor:
            error_msg = "Fornecedor não encontrado na base :/"
            logger.warning(f"Erro ao deletar fornecedor #{fornecedor_id}, {error_msg}")
            return {"message": error_msg}, 404  # Usamos 404 para indicar que o recurso não foi encontrado
        
        enderecos =[
            {
                "nome_fornecedor": fornecedor.nome,
                "endereco_id": endereco.id,
                "cep": endereco.cep,
                "tipo_endereco": endereco.tipo_endereco,
                "endereco": endereco.endereco,
                "cidade": endereco.cidade,
                "uf": endereco.uf,
            }
            for endereco in fornecedor.enderecos
        ]

        return jsonify(enderecos)

    except NoResultFound as e:
        error_msg = "Erro interno do servidor"
        logger.warning(f"Erro interno do servidor #{fornecedor_id}, {error_msg}")
        return {"message": error_msg}, 500  

@app.delete('/fornecedor_endereco', tags=[fornecedor_endereco_tag],
            responses={"200": FornecedorEnderecoDelSchema, "404": ErrorSchema})
def del_fornecedor_endereco(query: FornecedorEnderecoDeleteSchema):
    """Deleta um endereco de um fornecedor a partir do id informado

    Retorna uma mensagem de confirmação da remoção.
    """
    fornecedorEndereco_id   = query.id_end
    fornecedor_id           = query.fornecedor_id

    logger.debug(f"Deletando dados sobre endereço do fornecedor #{fornecedorEndereco_id}")
    session = Session()

    try:

        if fornecedorEndereco_id:

            count = (
                session.query(FornecedorEndereco)
                .filter(and_(FornecedorEndereco.id == fornecedorEndereco_id, \
                             FornecedorEndereco.fornecedor_id == fornecedor_id))
                .delete()
            )

        session.commit()

        if count:
            logger.debug(f"Deletado endereço do fornecedor #{fornecedor_id} endereço {fornecedorEndereco_id}")
            return {"mesage": "endereço do fornecedor removido", "id": fornecedor_id, "id_end":fornecedorEndereco_id}
        else: 
            error_msg = "fornecedor não encontrado na base :/"
            logger.warning(f"Erro ao deletar endereço do fornecedor #'{fornecedor_id}' id_end #'{fornecedorEndereco_id}', {error_msg}")
            return {"mesage": error_msg}, 400
        
    except NoResultFound:
        error_msg = "Fornecedor não encontrado na base :/"
        logger.warning(f"Erro ao deletar endereço do fornecedor #{fornecedor_id} id_end #{fornecedorEndereco_id}, {error_msg}")
        return {"message": error_msg}, 404  # Usamos 404 para indicar que o recurso não foi encontrado


@app.put('/fornecedor_endereco', tags=[fornecedor_endereco_tag],
         responses={"200": FornecedorEnderecoSchema, "404" : ErrorSchema})
def upd_fornecedorEndereco(query: FornecedorEnderecoPUTSchema):
    """Atualiza um endereço do fornecedor a partir do ID da Fornecedor e ID do endereço informado
    
    Retorna uma mensagem de confirmação da atualização
    """
    query = request.json_data

    # print(f"CEP: {query['cep']} CIDADE: {query['cidade']} ENDEREÇO: {query['endereco']} FORNECEDOR: {query['fornecedor_id']} ID: {query['id']}")

    endereco_cep            = query['cep']
    endereco_cidade         = query['cidade']
    endereco_endereco       = query['endereco']
    endereco_fornecedor_id  = query['fornecedor_id']
    endereco_id             = query['id']
    endereco_tipo_endereco  = query['tipo_endereco']
    endereco_uf             = query['uf']

    logger.debug(f"Atualizando dados sobre a endereço do fornecedor #{endereco_fornecedor_id}")

    # Criando conexão com a base
    session = Session()
    
    try:
        # Fazendo a busca pelo ID da Fornecedor e ID do endereço
        db_fornecedorEndereco = session.query(FornecedorEndereco) \
                                       .filter(and_(FornecedorEndereco.fornecedor_id == endereco_fornecedor_id, 
                                                    FornecedorEndereco.id == endereco_id)) \
                                       .first()

        if not db_fornecedorEndereco:
            # Se a Fornecedor não foi encontrado
            error_msg = f"Fornecedor não encontrada na base.\nDetalhe: {repr(e)}"
            logger.warning(f"Erro ao buscar o endereço do Fornecedor '{endereco_fornecedor_id}', {error_msg}")
            return {"message": error_msg}, 404
        else:

            db_fornecedorEndereco.cep           = endereco_cep
            db_fornecedorEndereco.cidade        = endereco_cidade
            db_fornecedorEndereco.endereco      = endereco_endereco
            db_fornecedorEndereco.tipo_endereco = endereco_tipo_endereco
            db_fornecedorEndereco.uf            = endereco_uf

            # Grava alteração
            session.add(db_fornecedorEndereco)

            # Gravando a atualização
            session.commit()

            logger.debug(f"Editado Fornecedor de ID: '{db_fornecedorEndereco.fornecedor_id}' endereço ID '{db_fornecedorEndereco.id}'")
            return apresenta_fornecedor_endereco(db_fornecedorEndereco), 200
        
    except IntegrityError as e:
        # Tratamento para erro de integridade do banco de dados
        error_msg = f"Fornecedor de mesmo nome já salvo na base :\n {repr(e)}"
        logger.error(f"Erro de integridade do banco de dados ao atualizar a Fornecedor: {error_msg}")
        return {"message": error_msg}, 500

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = f"Não foi possível salvar novo item.\nDetalhe: {repr(e)}"
        logger.warning(f"Erro ao adicionar Fornecedor '{db_fornecedorEndereco.nome}', {error_msg}")
        print(f"ERRO: {error_msg}")
        return {"message": error_msg}, 400




# -------------------------
#   MÉTODOS UTILITÁRIOS
#--------------------------


# Definição da função que verifica se os campos foram alterados
def upd_campo_modificados(campo, novo_valor):
    if novo_valor is not None and novo_valor != "" and campo != novo_valor:
        return novo_valor

    return campo  