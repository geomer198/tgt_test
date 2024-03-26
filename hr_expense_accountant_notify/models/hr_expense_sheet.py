from odoo import _, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def action_submit_sheet(self):
        result = super().action_submit_sheet()
        accountant_user = self.env.company.company_accountant_user_id
        if not accountant_user:
            return result
        # Subscribe accountant user to records
        for record in self:
            record.message_subscribe(partner_ids=accountant_user.partner_id.ids)
        return result

    def _do_approve(self):
        notification = super()._do_approve()
        accountant_user = self.env.company.company_accountant_user_id
        if not accountant_user:
            return notification
        # Notify accountant user
        for record in self:
            record.message_post(
                body=_("Expense Report approved by manager"),
                partner_ids=accountant_user.partner_id.ids,
            )
        return notification
