from odoo import fields, models , api

class EstateProperty(models.Model):
    
    _name = "estate.property"
    _description = "Real estate properties"


    name = fields.Char(string = "Title" , required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.add(fields.Date.today() , months = 3))
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


