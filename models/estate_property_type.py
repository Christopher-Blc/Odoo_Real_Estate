from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipo de propiedad"

    name = fields.Char(required=True)

    _sql_constraints = [
        ('check_unique_type_name', 'UNIQUE(name)', 'The type must be unique'),
    ]