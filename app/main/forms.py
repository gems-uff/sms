import wtforms as wtf
import wtforms.widgets.html5 as widgets
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import (DataRequired, InputRequired, NumberRange,
                                Optional)

from .models import Product, StockProduct, Transaction, Specification
from app.auth.models import User


class OrderItemForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        specs = kwargs.get('specs', [])
        self.item_id.choices = [
            (s.id, '{} | {} | Catálogo: {} | {} unidades/produto'.format(
                s.product.name,
                s.manufacturer,
                s.catalog_number,
                s.units)
             ) for s in specs
        ]

    item_id = wtf.SelectField(
        'Reativo', coerce=int, validators=[InputRequired()])
    amount = wtf.IntegerField(
        'Quantidade',
        widget=widgets.NumberInput(),
        render_kw={"autocomplete": "off"},
        validators=[
            InputRequired(),
            NumberRange(
                min=1, max=None, message='Quantidade deve ser maior que zero!')
        ])
    lot_number = wtf.StringField(
        'Lote',
        render_kw={"autocomplete": "off"},
        validators=[InputRequired()])
    expiration_date = wtf.DateField(
        'Data de Validade',
        widget=widgets.DateInput(),
        validators=[InputRequired()])
    add_product = wtf.SubmitField('Adicionar produto ao carrinho')
    finish_order = wtf.SubmitField('Ir para checkout')
    cancel = wtf.SubmitField('Limpar o carrinho')


class OrderForm(FlaskForm):
    invoice_type = wtf.SelectField(
        'Tipo de Nota',
        coerce=str,
        choices=(
            ('Não informado',
             'Não informado'),
            ('Nota Fiscal',
             'Nota Fiscal'),
            ('Nota de Fornecimento (FIOCRUZ)',
             'Nota de Fornecimento (FIOCRUZ)'),
            ('Nota de Fornecimento (Ministério da Saúde)',
             'Nota de Fornecimento (Ministério da Saúde)'),
            ('Outros',
             'Outros')),
        default='Não informado',
        validators=[Optional()])
    invoice = wtf.StringField('Nota', validators=[Optional()])
    invoice_value = wtf.FloatField(
        'Valor total',
        render_kw={'placeholder': 'R$ 123.40'},
        validators=[Optional()],
        widget=widgets.NumberInput(step='0.01', min='0.00', max='9999999999.99'))
    financier = wtf.StringField('Financiador', validators=[Optional()])
    notes = wtf.StringField('Observações', validators=[Optional()])
    submit = wtf.SubmitField('Inserir no estoque')
    cancel = wtf.SubmitField('Limpar o carrinho')


class ConsumeProductForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stock_products = kwargs.get('stock_products', [])
        self.stock_product_id.choices = [
            (sp.id, (f'''
                {sp.product.name}
                 | Lote: {sp.lot_number}
                 | Validade: {sp.expiration_date.strftime('%d-%m-%y')}
                 | Quantidade: {sp.amount}
                 | Fabricante: {sp.manufacturer}
            ''')) for sp in stock_products
        ]
        self.consumer_id.choices = [(user.id, user.email) for user in User.query.order_by(User.email).all()]

    stock_product_id = wtf.SelectField(
        'Reativo', coerce=int, validators=[InputRequired()])
    amount = wtf.IntegerField(
        'Quantidade',
        validators=[
            InputRequired(),
            NumberRange(
                min=1, max=None, message='Quantidade deve ser maior que zero!')
        ],
        widget=widgets.NumberInput(),
        render_kw={'autocomplete': 'off'},
        default=1,
    )
    consumer_id = wtf.SelectField(
        'Consumidor final',
        coerce=int,
        validators=[InputRequired()],
    )
    submit = wtf.SubmitField('Confirmar')


class AddProductForm(FlaskForm):
    name = wtf.StringField('Nome do reativo', validators=[InputRequired()])
    stock_minimum = wtf.IntegerField(
        'Alertar quando estoque atingir',
        default=1,
        validators=[
            InputRequired(),
            NumberRange(min=1, max=None, message='Deve ser maior que zero!')
        ],
        widget=widgets.NumberInput(),
        render_kw={'autocomplete': 'off'},
    )
    submit = wtf.SubmitField('Cadastrar Reativo')


class AddSpecificationForm(FlaskForm):
    def __init__(self, product_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id.data = product_id

    product_id = wtf.HiddenField()
    manufacturer = wtf.StringField('Fabricante', validators=[InputRequired()])
    catalog_number = wtf.StringField('Catálogo', validators=[InputRequired()])
    units = wtf.IntegerField('<a href="#" data-toggle="tooltip" title="Quantidade de unidades que essa apresentação possui. Representa a quantidade física dessa apresentação que será adicionada ao estoque quando comprado.">Unidades de estoque</a>',
                             default=1,
                             validators=[
                                 InputRequired(),
                                 NumberRange(min=1, max=None,
                                             message='Deve ser maior que zero!')
                             ],
                             widget=widgets.NumberInput(),
                             render_kw={'autocomplete': 'off'},
                             )
    submit = wtf.SubmitField('Confirmar')
