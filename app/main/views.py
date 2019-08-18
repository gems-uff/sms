# TODO: export logger from logger.py
import jsonpickle

from flask import (Blueprint, render_template, redirect,
                   url_for, current_app, session, request, flash)
import sqlalchemy
from flask_login import current_user

from app.extensions import db
from app.logger import logger
from app.auth.decorators import restrict_to_logged_users, permission_required
from app.auth.models import Permission, User
from .models import (
    Order, OrderItem, Transaction, Stock, StockProduct, Product, Specification)
from . import forms
from . import services as svc
from . import utils


blueprint = Blueprint('main', __name__)
blueprint.before_request(restrict_to_logged_users)


@blueprint.route('/', methods=['GET'])
@permission_required(Permission.VIEW)
def index():
    return redirect(url_for('.show_stock'))


@blueprint.route('/stock', methods=['GET'])
@permission_required(Permission.VIEW)
def show_stock():
    template = 'main/index.html'
    products = svc.get_products_in_stock(svc.get_stock())

    stock = svc.get_stock()
    stock_products = sorted(
        [sp for sp in stock.stock_products if sp.amount > 0],
        key=lambda sp: sp.product.name,
    )
    return render_template(template,
                           products=products,
                           stock_products=stock_products)


@blueprint.route('/catalog', methods=['GET'])
@permission_required(Permission.VIEW)
def show_catalog():
    template = 'main/list-products.html'
    view = 'main.show_catalog'
    products = Product.query.order_by(Product.name).all()
    return render_template(template,
                           products=products)


@blueprint.route('/transactions', methods=['GET'])
@permission_required(Permission.VIEW)
def list_transactions():
    template = 'main/list-transactions.html'
    view = 'main.list_transactions'
    transactions = Transaction.query.order_by(
        Transaction.updated_on.desc()).all()
    return render_template(template,
                           transactions=transactions)


@blueprint.route('/orders', methods=['GET'])
@permission_required(Permission.VIEW)
def list_orders():
    template = 'main/list-orders.html'
    view = 'main.list_orders'
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template(template,
                           orders=orders)


# TODO: Implement this method:
@blueprint.route('/transactions/<int:transaction_id>/delete', methods=['GET'])
@permission_required(Permission.DELETE)
def delete_transaction(transaction_id):
    flash('Essa funcionalidade ainda não foi implementada.', 'warning')
    return redirect(url_for('.list_transactions'))


@blueprint.route('/orders/add', methods=['GET', 'POST'])
@permission_required(Permission.EDIT)
def purchase_product():
    logger.info('purchase_product()')
    specifications = svc.get_specifications()
    form_context = {
        'specs': specifications,
    }
    form = forms.OrderItemForm(**form_context)

    order_items = svc.get_order_items_from_session()
    for order_item in order_items:
        order_item.item = Specification.query.get(order_item.item_id)

    if request.method == 'POST':
        if form.cancel.data is True:
            svc.clear_order_items_session()
            return redirect(url_for('.purchase_product'))
        if form.finish_order.data is True:
            if order_items:
                return redirect(url_for('.checkout'))
            flash('Pelo menos 1 reativo deve ser adicionado ao carrinho.',
                  'danger')
            return redirect(url_for('.purchase_product'))
        if form.validate():
            order_item = OrderItem()
            form.populate_obj(order_item)
            svc.add_order_item_to_session(order_item)
            flash('Reativo adicionado ao carrinho', 'success')
            return redirect(url_for('.purchase_product'))
    return render_template('main/create-order.html',
                           form=form, order_items=order_items)


@blueprint.route('/orders/checkout', methods=['GET', 'POST'])
@permission_required(Permission.EDIT)
def checkout():
    form = forms.OrderForm()
    stock = svc.get_stock()
    if session.get('order_items') is None:
        session['order_items'] = []
    order_items = [jsonpickle.decode(item)
                   for item in session.get('order_items')]
    for order_item in order_items:
        order_item.item = Specification.query.get(order_item.item_id)
    logger.info('Retrieve unpickled order_items from session')
    if request.method == 'POST':
        logger.info('POSTing to checkout')
        if form.cancel.data is True:
            logger.info('Cancel order, cleaning session')
            session['order_items'] = []
            return redirect(url_for('.purchase_product'))
        if order_items:
            if form.validate():
                logger.info('starting check out...')
                order = Order()
                logger.info(
                    'populating order with form data and order_items')
                form.populate_obj(order)
                order.order_items = order_items
                order.user = current_user
                db.session.add(order)
                try:
                    logger.info('Saving order to database...')
                    for order_item in order.order_items:
                        logger.info(
                            'Adding %s to stock' % order_item)
                        product = order_item.item.product
                        lot_number = order_item.lot_number
                        total_units = order_item.amount * order_item.item.units
                        expiration_date = order_item.expiration_date
                        logger.info('stock.add({}, {}, {}, {})'.format(
                            product, lot_number, expiration_date, total_units))
                        stock.add(
                            product,
                            lot_number,
                            expiration_date,
                            total_units)
                        order_item.added_to_stock = True
                        db.session.add(order_item)
                    logger.info('Comitting session...')
                    db.session.commit()
                    logger.info(
                        'Creating transactions from order...')
                    svc.create_add_transactions_from_order(order, stock)
                    logger.info(
                        'Flashing success and returning to index')
                    flash('Ordem executada com sucesso', 'success')
                    session['order_items'] = []
                    return redirect(url_for('.index'))
                except (ValueError) as err:
                    db.session.rollback()
                    session['order_items'] = []
                    logger.error('Could not save the order to db. Rollback.')
                    logger.error(err)
                    flash('Algo deu errado, contate um administrador!')
                    return render_template('main/index.html')
        else:
            logger.info('No item added to cart')
            flash('É necessário adicionar pelo menos 1 item ao carrinho.',
                  'warning')
            return redirect(url_for('.purchase_product'))
    return render_template('main/checkout.html',
                           form=form,
                           order_items=order_items,)


@blueprint.route('/products/consume', methods=['GET', 'POST'])
@permission_required(Permission.EDIT)
def consume_product():
    logger.info('consume_product()')
    stock = svc.get_stock()
    stock_products = sorted(
        [sp for sp in stock.stock_products if sp.amount > 0],
        key=lambda sp: sp.product.name,
    )
    for stock_product in stock_products:
        stock_product.manufacturer = svc.get_manufacturer_by_lot_number(stock_product.lot_number)
    form_context = {
        'stock_products': stock_products,
    }
    form = forms.ConsumeProductForm(**form_context)

    if form.validate_on_submit():
        logger.info('POSTing a valid form to consume_product')
        logger.info('Creating a new SUB Transaction')
        try:
            selected_stock_product = StockProduct.query.get(
                form.stock_product_id.data)
            logger.info(
                'Retrieving info from selected_stock_product')
            product = selected_stock_product.product
            lot_number = selected_stock_product.lot_number
            amount = form.amount.data
            stock.subtract(product, lot_number, amount)
            logger.info('Commiting subtraction')
            consumer_user = User.query.filter_by(email=form.consumer_email.data).first()
            db.session.commit()
            logger.info('Creating sub-transaction')
            svc.create_sub_transaction(
                consumer_user,
                product,
                lot_number,
                amount,
                stock
            )
            flash('{} unidades de {} removidas do estoque com sucesso!'.format(
                form.amount.data, selected_stock_product.product.name),
                'success',
            )

            return redirect(url_for('.consume_product'))
        except ValueError as err:
            logger.error(err)
            form.amount.errors.append(
                'Não há o suficiente desse reativo em estoque.')
        except Exception:
            flash('Erro inesperado, contate o administrador.', 'danger')

    return render_template('main/consume-product.html', form=form)


@blueprint.route('/products/add', methods=['GET', 'POST'])
@permission_required(Permission.EDIT)
def add_product_to_catalog():
    form = forms.AddProductForm()

    if form.validate_on_submit():
        product = svc.get_product_by_name(form.name.data)
        if product:
            flash('Já existe um reativo com esse nome no catálogo.\
                Segue abaixo suas especificações', 'warning')
        else:
            product = svc.create_product(form.name.data)
            flash(f'{product.name} adicionado ao catálogo com sucesso',
                  'success')
        return redirect(url_for('.detail_product',
                                product_id=product.id,
                                specifications=product.specifications))
    return render_template('main/create-product.html', form=form)


@blueprint.route('/products/<int:product_id>/specifications',
                 methods=['GET', 'POST'])
@permission_required(Permission.EDIT)
def add_specification_to_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = forms.AddSpecificationForm(product.id)
    if form.validate_on_submit():
        try:
            specification = Specification(
                catalog_number=form.catalog_number.data,
                manufacturer=form.manufacturer.data,
                units=form.units.data,
                product_id=product_id,
            )
            db.session.add(specification)
            db.session.commit()
            flash('Especificação adicionada com sucesso.', 'success')
            return redirect(url_for('.detail_product', product_id=product.id))
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            flash('Já existe uma especificação com esse catálogo e fabricante',
                  'danger')
    return render_template('main/create-specification.html',
                           form=form, product=product)


@blueprint.route('/products/<int:product_id>', methods=['GET'])
@permission_required(Permission.EDIT)
def detail_product(product_id):
    product = Product.query.get_or_404(product_id)
    specifications = sorted(
        [spec for spec in product.specifications],
        key=lambda spec: spec.units,
    )
    return render_template('main/details-product.html',
                           product=product,
                           specifications=specifications)


@blueprint.route('/export/<string:table>')
@permission_required(Permission.VIEW)
def export(table):
    response = utils.export_table(table, table + '.csv')
    return response
