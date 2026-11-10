Sale Commission Remove Item
===========================

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

.. description-start
This module allows removing the commission from sale order lines based on a
configurable rule.

A rule is defined by:

*   a product category,
*   a field of the sales order form,
*   the value of that field.

When a sale order line matches a rule (product in the category and the sales
order field set to the configured value), the commission is not applied to the
line.
.. description-end

.. install-start
Install this module as usual from the Odoo Apps list.
.. install-end

.. configure-start
To configure a commission removal rule:

1.  Go to *Commissions > Configuration > Remove Commission Items*.
2.  Click *Create*.
3.  Fill in the product category, the sales order field and the value that
    triggers the removal, then save.
.. configure-end

.. usage-start
When a sale order line matches an active rule, the field **Commission Removed**
is checked on the line and no commission is applied (commission amount is set
to zero and agents are removed from the line).
.. usage-end

.. contributors-start
- Rodrigo A. Madureira <https://github.com/rodmad85>
- [Madooit](https://madooit.com)
.. contributors-end

.. changelog-start
18.0.1.0.0: Initial release.
.. changelog-end

.. roadmap-start
.. roadmap-end
