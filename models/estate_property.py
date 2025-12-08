from odoo import fields, models
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    
    _name = "estate.property"
    _description = "Real estate properties"


    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Datetime(default=lambda self: fields.Datetime.now() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(
    readonly=True,
    copy=False
    )
    bedrooms = fields.Integer(
    default=2
    )
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection =[('north', 'North'), ('south', 'South') , ('east', 'East') , ('west', 'West')],
        string = 'garden_orientation'
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
                ('new', 'New'),
                ('offer_received', 'Offer Received'),
                ('offer_accepted', 'Offer Accepted'),
                ('sold', 'Sold'),
                ('cancelled', 'Cancelled')
            ],        
        string = 'State',
        copy=False,
        default='new',
        required=True,
    )
