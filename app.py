# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from models import db, Cliente, Produto, Venda, app

UPLOAD_FOLDER = 'static/imagens_produtos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    vendas = Venda.query.all()
    return render_template('index.html', clientes=clientes, produtos=produtos, vendas=vendas)

# Rotas para Cliente


@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = int(request.form['idade'])
        cpf = request.form['cpf']
        email = request.form['email']
        endereco = request.form['endereco']

        novo_cliente = Cliente(nome=nome, idade=idade,
                               cpf=cpf, email=email, endereco=endereco)
        db.session.add(novo_cliente)
        db.session.commit()
        flash("Cliente cadastrado com sucesso!")
        return redirect(url_for('index'))

    return render_template('cadastro_cliente.html')


@app.route('/cliente/<int:id>')
def visualizar_cliente(id):
    cliente = Cliente.query.get(id)
    return render_template('visualizar_cliente.html', cliente=cliente)


@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.idade = int(request.form['idade'])
        cliente.cpf = request.form['cpf']
        cliente.email = request.form['email']
        cliente.endereco = request.form['endereco']
        db.session.commit()
        flash("Cliente atualizado com sucesso!")
        return redirect(url_for('index'))
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/deletar_cliente/<int:id>')
def deletar_cliente(id):
    cliente = Cliente.query.get(id)
    vendas_associadas = Venda.query.filter_by(cliente_id=id).first()

    if vendas_associadas:
        flash("Não é possível deletar o cliente, pois existem vendas associadas a ele.")
        return redirect(url_for('index'))

    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente deletado com sucesso!")
    return redirect(url_for('index'))


# Rotas para Produto
@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        quantidade_estoque = int(request.form['quantidade_estoque'])
        imagem = request.files['imagem']

        imagem_filename = secure_filename(imagem.filename)
        imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], imagem_filename))

        novo_produto = Produto(nome=nome, preco=preco, descricao=descricao,
                               quantidade_estoque=quantidade_estoque, imagem=imagem_filename)
        db.session.add(novo_produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!")
        return redirect(url_for('index'))

    return render_template('cadastro_produto.html')


@app.route('/produto/<int:id>')
def visualizar_produto(id):
    produto = Produto.query.get(id)
    return render_template('visualizar_produto.html', produto=produto)


@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.preco = float(request.form['preco'])
        produto.descricao = request.form['descricao']
        produto.quantidade_estoque = int(request.form['quantidade_estoque'])
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem:
                imagem_filename = secure_filename(imagem.filename)
                imagem.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], imagem_filename))
                produto.imagem = imagem_filename
        db.session.commit()
        flash("Produto atualizado com sucesso!")
        return redirect(url_for('index'))
    return render_template('editar_produto.html', produto=produto)


@app.route('/deletar_produto/<int:id>')
def deletar_produto(id):
    produto = Produto.query.get(id)
    vendas_associadas = Venda.query.filter_by(produto_id=id).first()

    if vendas_associadas:
        flash("Não é possível deletar o produto, pois existem vendas associadas a ele.")
        return redirect(url_for('index'))

    db.session.delete(produto)
    db.session.commit()
    flash("Produto deletado com sucesso!")
    return redirect(url_for('index'))


# Rotas para Venda
@app.route('/cadastrar_venda', methods=['GET', 'POST'])
def cadastrar_venda():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])

        produto = Produto.query.get(produto_id)
        if produto.quantidade_estoque < quantidade:
            flash("Estoque insuficiente para a venda.")
            return redirect(url_for('cadastrar_venda'))

        produto.quantidade_estoque -= quantidade
        nova_venda = Venda(cliente_id=cliente_id,
                           produto_id=produto_id, quantidade=quantidade)
        db.session.add(nova_venda)
        db.session.commit()
        flash("Venda registrada com sucesso!")
        return redirect(url_for('index'))

    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('cadastrar_venda.html', clientes=clientes, produtos=produtos)


@app.route('/venda/<int:id>')
def visualizar_venda(id):
    venda = Venda.query.get(id)
    return render_template('visualizar_venda.html', venda=venda)


@app.route('/editar_venda/<int:id>', methods=['GET', 'POST'])
def editar_venda(id):
    venda = Venda.query.get(id)
    if request.method == 'POST':
        venda.cliente_id = request.form['cliente_id']
        venda.produto_id = request.form['produto_id']
        venda.quantidade = int(request.form['quantidade'])

        produto = Produto.query.get(venda.produto_id)
        if produto.quantidade_estoque < venda.quantidade:
            flash("Estoque insuficiente para a venda.")
            return redirect(url_for('editar_venda', id=id))

        db.session.commit()
        flash("Venda atualizada com sucesso!")
        return redirect(url_for('index'))

    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('editar_venda.html', venda=venda, clientes=clientes, produtos=produtos)


@app.route('/deletar_venda/<int:id>')
def deletar_venda(id):
    venda = Venda.query.get(id)
    db.session.delete(venda)
    db.session.commit()
    flash("Venda deletada com sucesso!")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'
    app.run(debug=True)
