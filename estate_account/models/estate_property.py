from odoo import models, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        res = super().action_sold()

        for prop in self:
            # 1) Crear factura vacia (account.move)
            move = self.env["account.move"].create({
                "partner_id": prop.buyer_id.id,      # cliente
                "move_type": "out_invoice",          # customer invoice
                "invoice_line_ids": [
                    # 2) Linea 6% del precio de venta
                    Command.create({
                        "name": prop.name,
                        "quantity": 1,
                        "price_unit": prop.selling_price * 0.06,
                    }),
                    # 3) Linea de 100.00
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1,
                        "price_unit": 100.0,
                    }),
                ],
            })

        return res
