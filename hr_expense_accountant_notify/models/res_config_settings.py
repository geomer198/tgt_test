from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    accountant_user_id = fields.Many2one(
        comodel_name="res.users",
        related="company_id.company_accountant_user_id",
        readonly=False,
    )
