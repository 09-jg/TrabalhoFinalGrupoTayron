# models.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)

    def __init__(self, nome, idade, cpf, email, endereco):
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
        self.email = email
        self.endereco = endereco

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)
    imagem = db.Column(db.String(100), nullable=True)  # Nome do arquivo de imagem

    def __init__(self, nome, preco, descricao, quantidade_estoque, imagem):
        self.nome = nome
        self.preco = preco
        self.descricao = descricao
        self.quantidade_estoque = quantidade_estoque
        self.imagem = imagem

    @staticmethod
    def validar_nome(nome):
        return len(nome) >= 3

    @staticmethod
    def validar_preco(preco):
        return preco > 0

class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

    cliente = db.relationship('Cliente', backref=db.backref('vendas', lazy=True))
    produto = db.relationship('Produto', backref=db.backref('vendas', lazy=True))

    def __init__(self, cliente_id, produto_id, quantidade):
        self.cliente_id = cliente_id
        self.produto_id = produto_id
        self.quantidade = quantidade

with app.app_context():
    db.create_all()