To configure a commission removal rule:

1.  Go to *Commissions > Configuration > Remove Commission Items*.
2.  Click *Create*.
3.  Fill in:
    *   **Name**: description of the rule.
    *   **Product Category**: category the rule applies to (child categories are
        included).
    *   **Sale Order Field**: field of the sales order form to evaluate. All
        fields of the sale order form are available for selection.
    *   **Value**: value of the selected field that triggers the removal. For
        relational fields, use the record id or its name.
    *   **Active**: uncheck to disable the rule without deleting it.
4.  Save.

When a sale order line matches an active rule, the field **Commission Removed**
is checked on the line and no commission is applied (the commission amount is
set to zero and the agents are removed from the line).
