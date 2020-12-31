# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"

    @api.model
    def set_order_paid(self, paymentData):
        """Make the order Paid in Odoo via requests from XML-RPC
        @param paymentData: A standard dictionary consisting of 'order_id', 'journal_id', 'amount'
        @param context: A Dictionary with key 'ecommerce' to identify the request from E-Commerce
        @return:  A dictionary of status and status message of transaction"""
        ctx = dict(self._context or {})
        status = True
        counter = 0
        draftInvoiceIds = []
        invoiceId = False
        ecommerceInvoiceId = False
        statusMessage = "Payment Successfully made for Order."
        try:
            # Turn off active connection so that invoice sync will stop from odoo
            journalId = paymentData.get('journal_id', False)
            saleObj = self.env['sale.order'].browse(
                paymentData.get('order_id'))
            if not saleObj.invoice_ids:
                ecommerceInvoiceId = paymentData.get('ecommerce_invoice_id')
                createInvoice = self.create_order_invoice(
                    paymentData.get('order_id'), ecommerceInvoiceId)
                if createInvoice['status']:
                    draftInvoiceIds.append(createInvoice['invoice_id'])
            elif saleObj.invoice_ids:
                # currently supporting only one invoice per sale order to be
                # paid
                for invoiceObj in saleObj.invoice_ids:
                    if invoiceObj.state == 'posted':
                        invoiceId = invoiceObj.id
                    elif invoiceObj.state == 'draft':
                        draftInvoiceIds.append(invoiceObj.id)
                    counter += 1
            if counter <= 1:
                if draftInvoiceIds:
                    invoiceId = draftInvoiceIds[0]
                    invoiceObj = self.env[
                        'account.move'].browse(invoiceId).action_post()
                # Setting Context for Payment Wizard
                ctxDict = dict(
                    default_invoice_ids=[[4, invoiceId, None]],
                    active_model='account.move',
                    journal_type='sale',
                    search_disable_custom_filters=True,
                    active_ids=[invoiceId],
                    type='out_invoice',
                    active_id=invoiceId
                )
                ctx.update(ctxDict)
                # Getting all default field values for Payment Wizard
                paymentFields = [
                    'communication',
                    'currency_id',
                    'invoice_ids',
                    'payment_difference',
                    'partner_id',
                    'payment_method_id',
                    'payment_difference_handling',
                    'journal_id',
                    'state',
                    'writeoff_account_id',
                    'payment_date',
                    'partner_type',
                    'hide_payment_method',
                    'payment_method_code',
                    'amount',
                    'payment_type']
                defaultVals = self.env['account.payment'].with_context(
                    ctx).default_get(paymentFields)
                paymentMethodId = self.with_context(
                    ctx).get_default_payment_method(journalId)
                defaultVals.update(
                    {'journal_id': journalId, 'payment_method_id': paymentMethodId})
                invoiceDate = self.env['account.move'].browse(
                    invoiceId).invoice_date
                defaultVals['payment_date'] = invoiceDate
                payment = self.env['account.payment'].create(defaultVals)
                paid = payment.post()
            else:
                status = False
                statusMessage = "Multiple validated Invoices found for the Odoo order. Cannot make Payment"
        except Exception as e:
            statusMessage = "Error in creating Payments for Invoice: %s" % str(
                e)
            status = False
        finally:
            return {
                'status_message': statusMessage,
                'status': status
            }

    @api.model
    def create_order_invoice(self, orderId, ecommerceInvoiceId=False):
        """Creates Order Invoice by request from XML-RPC.
        @param order_id: Odoo Order ID
        @return: a dictionary containig Odoo Invoice IDs and Status with Status Message
        """
        context = dict(self._context or {})
        invoiceId = False
        status = True
        statusMessage = "Invoice Successfully Created."
        try:
            saleObj = self.env['sale.order'].browse(orderId)
            invoiceId = saleObj.invoice_ids
            if saleObj.state == 'draft':
                self.confirm_odoo_order(orderId)
            if not invoiceId:

                invoiceId = saleObj._create_invoices()
                if ecommerceInvoiceId and invoiceId:
                    invoiceId.write({'name': ecommerceInvoiceId})
            else:
                statusMessage = "Invoice Already Created"
        except Exception as e:
            status = False
            statusMessage = "Error in creating Invoice: %s" % str(e)
        finally:
            if invoiceId:
                invoiceId = invoiceId[0].id
            else:
                invoiceId = 0
            return {
                'status': status,
                'status_message': statusMessage,
                'invoice_id': invoiceId
            }

    @api.model
    def get_default_payment_method(self, journalId):
        """ @params journal_id: Journal Id for making payment
                @params context : Must have key 'ecommerce' and then return payment payment method based on Odoo Bridge used else return the default payment method for Journal
                @return: Payment method ID(integer)"""
        paymentMethodObjs = self.env['account.journal'].browse(
            journalId)._default_inbound_payment_methods()
        if paymentMethodObjs:
            return paymentMethodObjs[0].id
        return False
