from odoo.tests import tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged("post_install", "-at_install")
class TestHrExpenseSheet(TestExpenseCommon):
    def setUp(self):
        super().setUp()
        self.expense1 = self.env["hr.expense"].create(
            {
                "name": "Dinner with client - Expenses",
                "employee_id": self.expense_employee.id,
                "product_id": self.product_a.id,
                "unit_amount": 350.00,
            }
        )
        self.expense2 = self.env["hr.expense"].create(
            {
                "name": "Team building at Huy",
                "employee_id": self.expense_employee.id,
                "product_id": self.product_a.id,
                "unit_amount": 2500.00,
            }
        )

    def _get_record_following_partners(self, record):
        """Get Following partners for record"""
        return (
            self.env["mail.followers"]
            .search([("res_model", "=", record._name), ("res_id", "=", record.id)])
            .mapped("partner_id")
        )

    def test_expense_sheet_submit_flow(self):
        """Test flow that check adding accounting user to expense sheet record"""
        self.env.company.company_accountant_user_id = self.expense_user_manager

        expense_sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense #1",
                "employee_id": self.expense_employee.id,
                "expense_line_ids": self.expense1,
            }
        )

        partners = self._get_record_following_partners(expense_sheet)

        self.assertNotIn(
            self.expense_user_manager.partner_id.id,
            partners.ids,
            "Expense user manager must not be contains in followers",
        )

        expense_sheet.action_submit_sheet()
        partners = self._get_record_following_partners(expense_sheet)

        self.assertIn(
            self.expense_user_manager.partner_id,
            partners,
            "Expense user manager must be contains in followers",
        )

        self.env.company.company_accountant_user_id = False

        expense_sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense #2",
                "employee_id": self.expense_employee.id,
                "expense_line_ids": self.expense2,
            }
        )

        partners = self._get_record_following_partners(expense_sheet)
        self.assertNotIn(
            self.expense_user_manager.partner_id.id,
            partners.ids,
            "Expense user manager must not be contains in followers",
        )

        expense_sheet.action_submit_sheet()
        partners = self._get_record_following_partners(expense_sheet)

        self.assertNotIn(
            self.expense_user_manager.partner_id,
            partners,
            "Expense user manager must not be contains in followers",
        )

    def test_expense_sheets_approve_flow(self):
        """
        Test flow that check creating notification message
        for accounting user
        """
        self.env.company.company_accountant_user_id = self.expense_user_manager

        expense_sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense #1",
                "employee_id": self.expense_employee.id,
                "expense_line_ids": self.expense1,
            }
        )
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()

        message = self.env["mail.message"].search(
            [
                ("res_id", "=", expense_sheet.id),
                ("model", "=", expense_sheet._name),
                ("partner_ids", "in", self.expense_user_manager.partner_id.ids),
            ]
        )
        self.assertTrue(message, "Message must be exists")
        self.assertIn(
            "Expense Report approved by manager",
            message.body,
            "Message body must be the same",
        )
