from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Oferta"

    price = fields.Float(required=True)

    validity = fields.Integer(
        default=7
    )

    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline"
    )

    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
        ondelete="cascade"
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = (
                    record.create_date.date() + timedelta(days=record.validity)
                )
            else:
                record.date_deadline = False

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days


    def action_accept(self):
        for offer in self:
            if offer.property_id.state == "sold":
                raise UserError("You cannot accept an offer on a sold property.")

            # Solo una oferta aceptada por propiedad
            accepted_offer = offer.property_id.offer_ids.filtered(
                lambda o: o.status == "accepted"
            )
            if accepted_offer:
                raise UserError("Only one offer can be accepted per property.")

            offer.status = "accepted"
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.property_id.state = "offer_accepted"

    def action_refuse(self):
        for offer in self:
            offer.status = "refused"

                

    
