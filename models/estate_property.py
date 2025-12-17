from odoo import fields, models , api 
from odoo.exceptions import UserError , ValidationError
from odoo.tools import float_compare, float_is_zero



class EstateProperty(models.Model):
    
    _name = "estate.property"
    _description = "Real estate properties"


    name = fields.Char(string = "Title" , required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.add(fields.Date.today() , months = 3))
    expected_price = fields.Float(required=True , _check_expected_price=True)
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
        string = 'Garden orientation'
    )

    #onchanged del garden 
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

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
        readonly=True 
        
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer"
    )

    salesman_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user
    )

    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags"
    )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers"
    )

    #Chapter 8 (campo calculado para el area total que es suma del garden y living area)
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area"
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    #Chapter 8 (campo calculado para variable almacenable best offer que se actualiza y se guarda))
    best_offer = fields.Float(
        string="Best Offer",
        compute="_compute_best_offer",
        store=True
    )

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_offer = max(prices) if prices else 0.0


    #Chapter 9 (accioes para botones para cambiar estado de la propiedad)
    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("A cancelled property cannot be sold.")
            record.state = "sold"

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("A sold property cannot be cancelled.")
            record.state = "cancelled"

    # SQL constraints
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.'),
    ]

    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if float_compare(record.expected_price, 0, precision_digits=2) <= 0:
                raise ValidationError(("The expected price must be strictly positive."))

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # Only check if selling_price is set (i.e., property has been sold)
            if not float_is_zero(record.selling_price, precision_digits=2):
                min_price = record.expected_price * 0.9
                if float_compare(record.selling_price, min_price, precision_digits=2) < 0:
                    raise ValidationError(
                        ("The selling price cannot be lower than 90%% of the expected price. "
                          "Expected: %.2f, Minimum allowed: %.2f, Got: %.2f") % 
                        (record.expected_price, min_price, record.selling_price)
                    )