from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _domain_company_accountant_user(self):
        """Prepare domain for accountant user"""
        return [
            ("company_id", "=", self.env.company.id),
            (
                "groups_id",
                "in",
                [
                    self.env.ref("hr_expense.group_hr_expense_user").id,
                    self.env.ref("account.group_account_invoice").id,
                ],
            ),
        ]

    company_accountant_user_id = fields.Many2one(
        comodel_name="res.users",
        check_company=True,
        domain=_domain_company_accountant_user,
    )
