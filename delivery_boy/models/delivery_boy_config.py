# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
_logger = logging.getLogger(__name__)

from odoo import models,fields,api,SUPERUSER_ID, _
import random, json, re
from .fcmAPI import FCMAPI

def _get_image_url(base_url, model_name, record_id, field_name, write_date=0, width=0, height=0 ):
    """
    Returns a local url that points to the image field of a given browse record.
    """
    if base_url and not base_url.endswith("/"):
        base_url = base_url+"/"
    if width or height:
        return '%sweb/image/%s/%s/%s/%sx%s?unique=%s'% (base_url, model_name, record_id, field_name, width, height, re.sub('[^\d]','',write_date))
    else:
        return '%sweb/image/%s/%s/%s?unique=%s'% (base_url, model_name, record_id, field_name, re.sub('[^\d]','',write_date))

class DeliveryBoyConfig(models.Model):
    _name = 'delivery.boy.config'
    _description = 'delivery boy config'

    def _default_language(self):
        lc = self.env['ir.default'].get('res.partner', 'lang')
        dl = self.env['res.lang'].search([('code', '=', lc)], limit=1)
        return dl.id if dl else self.env['res.lang'].search([]).ids[0]

    def _active_languages(self):
        return self.env['res.lang'].search([]).ids

    def _getDeliveryBoyProgram(self):
        res_config = self.env['res.config.settings'].sudo().get_db_configuration()
        self.db_program_id = res_config['program'] and res_config['program'].id

    name = fields.Char('Title', default="Delivery Boy Configuration", required=1)
    api_key = fields.Char(string='API Secret key', default="dummySecretKey", required=1)
    default_lang = fields.Many2one('res.lang', string='Default Language', default=_default_language,
                            help="If the selected language is loaded in the Delivery Boy, all documents related to "
                            "this contact will be printed in this language. If not, it will be English.")

    language_ids = fields.Many2many('res.lang', 'delivery_boy_lang_rel', 'delivery_boy_id', 'lang_id', 'Languages', default=_active_languages)
    db_program_id = fields.Many2one('delivery.boy.programs', compute="_getDeliveryBoyProgram")
    db_reset_password = fields.Boolean(string='Enable pwd reset', help="This allows users to trigger a password reset from App")
    show_banner = fields.Boolean(help="Allow this to show the delivery boy banner in App")
    verify_token = fields.Boolean(help="Before delivery confirmation of any picking delivery token will be verified")
    db_banner = fields.Binary('Banner')

    fcm_api_key = fields.Char(string='FCM Api key')

    def check_delivery_boy_addons(self):
        result = {}
        ir_model_obj = self.env['ir.module.module'].sudo()
        return result

    def _get_currency(self):
        response = {}
        try:
            self.ensure_one()
            response = {
            'code': self.db_program_id.currency_id.name,
            'symbol': self.db_program_id.currency_id.symbol,
            'position': self.db_program_id.currency_id.position
            }
        except Exception:
            pass

        return response

    @api.model
    def _validate(self, api_key,context=None):
        context = context or {}
        response = {'success':False, 'responseCode':400, 'message':_('Unknown Error !!!')}
        if not api_key:
            response['responseCode'] = 401
            response['message'] = _('Invalid/Missing Api Key !!!')
            return response
        try:
            # Get Delivery Boy Configuration
            delivery_boy_config = self.env['delivery.boy.config'].sudo().search([], limit=1)
            if not delivery_boy_config:
                response['responseCode'] = 501
                response['message'] = _("Delivery Boy Configuration not found !!!")
            elif delivery_boy_config.api_key != api_key:
                response['responseCode'] = 401
                response['message'] = _("API Key is invalid !!!")
            else:
                response['success'] = True
                response['responseCode'] = 200
                response['message'] = _('Login successfully.')
                response['lang'] = context.get('lang') or delivery_boy_config.default_lang and delivery_boy_config.default_lang.code or "en_US"
                response['currency'] = delivery_boy_config._get_currency()
                #local data should be removed when sending the final response from controller
                company_id = self.env['res.company'].sudo().search([], limit=1)
                response['local'] = {
                    'deliveryBoyProgram_obj': delivery_boy_config.db_program_id,
                    'lang_obj':self.env['res.lang']._lang_get(response['lang']),
                    'tz': 'Asia/Bahrain',
                    'allowed_company_ids':[company_id.id],
                    'default_company_id':company_id.id,
                    'lang':response['lang'],
                }
                response['addons'] = self.check_delivery_boy_addons()
        except Exception as e:
            response['responseCode'] = 400
            response['message'] = _("Login Failed:")+"%r"%e
        return response

    @api.model
    def _get_image_url(self, model_name, record_id, field_name, write_date=0, width=0, height=0, context=None):
        """ Returns a local url that points to the image field of a given browse record. """
        context = context or {}
        if context.get('base_url',"") and not context['base_url'].endswith("/"):
            context['base_url'] = context['base_url'] + "/"
        if width or height:
            return '%sweb/image/%s/%s/%s/%sx%s?unique=%s'% (context.get('base_url'), model_name, record_id, field_name, width, height, re.sub('[^\d]','',write_date))
        else:
            return '%sweb/image/%s/%s/%s?unique=%s'% (context.get('base_url'), model_name, record_id, field_name, re.sub('[^\d]','',write_date))

    @api.model
    def fetch_user_info(self, user_obj, context=None):
        context = context or {}
        temp_i = {
        'deliveryBoyProfileImage': self._get_image_url('res.partner',user_obj.partner_id.id,'image_1920', user_obj.partner_id.write_date.__str__(), context=context),
        'deliveryBoyName': user_obj.partner_id.name or "",
        'deliveryBoyEmail': user_obj.login or "",
        }
        return temp_i

    @api.model
    def getDefaultData(self):
        try:
            self.ensure_one()
        except ValueError:
            self = self.sudo().search([], limit=1)
        temp={}
        res_config = self.env['res.config.settings'].sudo().get_db_configuration()
        temp['allowCommission'] = res_config['allow_db_program']
        temp['allowResetPwd'] = self.db_reset_password
        temp['showBanner'] = self.show_banner
        temp['verifyToken'] = self.verify_token
        if self.show_banner:
            temp['bannerImage'] = self._get_image_url('delivery.boy.config',self.id,'db_banner', self.write_date.__str__(), context = {'base_url':self._context.get('base_url')})
        return temp

    @api.model
    def authenticate(self, credentials, detailed = False, isSocialLogin=False, context=None):
        context = context or {}
        response = {'success':False, 'responseCode':400, 'message':_('Unknown Error !!!')}
        user = False
        if not isinstance(credentials, dict):
            response['message'] = _('Data is not in Dictionary format !!!')
            return response
        if isSocialLogin:
            if not all(k in credentials for k in ('authProvider','authUserId')):
                response['message'] = _('Insufficient data to authenticate !!!')
                return response
            provider = self._getAuthProvider(credentials['authProvider'])
            try:
                user = self.env['res.users'].sudo().search([('oauth_uid', '=', credentials['authUserId']),('oauth_provider_id', '=', provider),('partner_id.is_delivery_boy','=',True)])
                if not user:
                    response['responseCode'] = 404
                    response['message'] = _("Social-Login: No such record found.")
            except Exception as e:
                response['message'] = _("Social-Login Failed")
                response['details'] = "%r"%e
        else:
            if not all(k in credentials for k in ('login','pwd')):
                response['message'] = _('Insufficient data to authenticate !!!')
                return response
            try:
                user = self.env['res.users'].sudo().search([('login', '=', credentials['login']),('partner_id.is_delivery_boy','=',True)])
                if user:

                    user.with_user(user.id)._check_credentials(credentials['pwd'])
                else:
                    response['responseCode'] = 400
                    response['message'] = _("Invalid password/email address.")
            except Exception as e:
                user = False
                response['responseCode'] = 400
                response['message'] = _("Login Failed")
                response['details'] = "%r"%e
        if user:
            try:
                response['success'] = True
                response['responseCode'] = 200
                response['deliveryBoyPartnerId'] = user.partner_id.id
                response['status'] = user.partner_id.delivery_boy_status
                response['userId'] = user.id
                response['message'] = _('Login successfully.')
                if detailed:
                    response.update(self.fetch_user_info(user, context=context))
            except Exception as e:
                response['responseCode'] = 400
                response['message'] = _("Login Failed")
                response['details'] = "%r"%e
        return response

    def _getCustomerDetails(self, db_picking):
        customer_details={
        'customerName': db_picking.picking_id and db_picking.picking_id.partner_id and db_picking.picking_id.partner_id.name or '',
        'customerDisplayAddress':db_picking.picking_id and db_picking.picking_id.partner_id and db_picking.picking_id.partner_id._display_address() or '',
        'phone':db_picking.picking_id and db_picking.picking_id.partner_id and db_picking.picking_id.partner_id.phone or '',
        'mobile':db_picking.picking_id and db_picking.picking_id.partner_id and db_picking.picking_id.partner_id.mobile or '',
        'customerEmail':db_picking.picking_id and db_picking.picking_id.partner_id and db_picking.picking_id.partner_id.email or '',
        'customerAddress':self._getAddress(db_picking),
        }
        return customer_details

    def _getPickingDetails(self, db_picking):
        details = {
        'id':db_picking.id or '',
        'name':db_picking.name or '',
        'assignedDate':db_picking.assigned_date and db_picking.assigned_date.strftime('%Y-%m-%d') or '',
        'assignedTime':db_picking.assigned_date and db_picking.assigned_date.strftime('%H:%M:%S') or '',
        'orderUntaxedAmount':self._formattedValue(
            db_picking.sale_order_id and db_picking.sale_order_id.amount_untaxed or 0.00,
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.symbol or '',
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.position or ''
        ),
        'orderTaxAmount':self._formattedValue(
            db_picking.sale_order_id and db_picking.sale_order_id.amount_tax or 0.00,
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.symbol or '',
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.position or ''
         ),
        'orderTotal':self._formattedValue(
            db_picking.sale_order_id and db_picking.sale_order_id.amount_total or 0.00,
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.symbol or '',
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.position or ''
        ),
        'hasCOD': False,
        'products': [],
        'pickingId': db_picking.picking_id.id or '',
        'pickingState': db_picking.picking_state or '',
        'commissionDate': db_picking.commission_date and db_picking.commission_date.__str__() or '',
        'commissionAmount':  self._formattedValue(
            db_picking.commission_amount or 0.00,
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.symbol or '',
            db_picking.sale_order_id and db_picking.sale_order_id.currency_id.position or ''
        ),
        }
        details.update(self._getCustomerDetails(db_picking))

        if not db_picking.sale_order_id:
            for move in db_picking.picking_id.move_ids_without_package:
                productDetails = self._productDetails(move.product_id)
                productDetails['deliverQty'] = move.product_uom_qty
                productDetails['salesPrice'] = self._formattedValue(0.00, '', '')
                productDetails['discount'] = self._formattedValue(0.00, "%")
                details['products'].append(productDetails)
        else:
            for line_id in db_picking.sale_order_id.order_line:
                productDetails = self._productDetails(line_id.product_id)
                productDetails['deliverQty'] = line_id.product_uom_qty
                productDetails['salesPrice'] = self._formattedValue(
                    line_id.price_unit,
                    line_id.currency_id.symbol,
                    line_id.currency_id.position
                )
                productDetails['discount'] = self._formattedValue(line_id.discount, "%")
                details['products'].append(productDetails)

        return details

    def _getAddress(self, db_picking):
        partner = db_picking.picking_id.partner_id

        customer_address = "%s,%s,%s,%s,%s,%s"%(
        partner.street or '',
        partner.street2 or '',
        partner.city or '',
        partner.state_id and partner.state_id.name or '',
        partner.zip or '',
        partner.country_id and partner.country_id.name or '',
        )
        return customer_address

    def _formattedValue(self, value, symbol, position='after'):
        if position != 'after':
            return "%s%d"%(symbol, value)
        return "%d%s"%(value, symbol)

    def _productDetails(self, product_id):
        result = {
        'name': product_id.name,
        # 'salesPrice':self._formattedValue(sale_id and sale_id.list_price or 0.00, self._get_currency().get('symbol')),
        'attributes':[],
        'image': self._get_image_url('product.product',product_id.id, 'image_128', product_id.write_date.__str__(), context = {'base_url':self._context.get('base_url')}),
        }
        for attribute_value_id in product_id.product_template_attribute_value_ids:
            result['attributes'].append({
            'name':attribute_value_id.attribute_id.name,
            'value':attribute_value_id.name
            })
        return result

    @api.model
    def getDeliveryBoyPickings(self, partner_id = False, db_picking_id = False, state = [], picking_state_categorise= True, **kwargs):
        domain = []

        db_pickings = self.env['delivery.boy.pickings'].sudo()
        result = picking_state_categorise and {selection[0]:[] for selection in db_pickings._fields['picking_state'].selection} or []
        if partner_id:
            domain.append(('partner_id','=',partner_id))
        if db_picking_id:
            domain.append(('id','=',db_picking_id))
        if state:
            domain.append(('picking_state','in',state))

        for db_picking in db_pickings.search(domain, offset = kwargs.get('offset'), limit = kwargs.get('limit'), order = kwargs.get('order') or 'id desc'):
            if picking_state_categorise:
                result[db_picking.picking_state].append(self._getPickingDetails(db_picking))
            else:
                result.append(self._getPickingDetails(db_picking))


        if db_picking_id:
            result = result.get(db_picking.picking_state)[0]

        return result


    @api.model
    def resetPassword(self, login):
        response = {'success':False, 'responseCode': 400}
        try:
            res_users = self.env['res.users'].sudo()
            if login:
                user = res_users.search([('login','=',login)])
                if user:
                    if user.partner_id.is_delivery_boy:
                        res_users.reset_password(login)
                        response['responseCode'] = 200
                        response['success'] = True
                        response['message'] = _("An email has been sent with credentials to reset your password")
                    else:
                        response['message']=_('User is not registered as a delivery boy.')
                else:
                    raise Exception
            else:
                response['message'] = _("No login provided.")
        except Exception as e:
            response['message'] = _("Invalid Username/Email.")
        return response

class DeliveryBoyPushNotificationTemplate(models.Model):
    _name = 'delivery.boy.push.notification.template'
    _description = 'Delivery Boy Push Notification Templates'
    _order = "name"

    def _addMe(self, data):
        _id = self.env["delivery.boy.notification.messages"].sudo().create(data)
        return True

    def _get_key(self):
        delivery_boy_config = self.env['delivery.boy.config'].sudo().search([], limit=1)
        return delivery_boy_config and delivery_boy_config.fcm_api_key or ""

    @api.model
    def _pushMe(self,key, payload_data, data=False):
        status = True
        summary = ""
        # _logger.info("---------------payload_data------------%r---", payload_data)
        try:
            push_service = FCMAPI(api_key=key)
            summary = push_service.send([payload_data])
            if data:
            	self._addMe(data)
        except Exception as e:
            status = False
            summary = "Error: %r"%e
        return [status,summary]

    def _customize_notification_title(self, db_picking):
        return re.sub("_",db_picking and db_picking.name or "",self.notification_title)

    def _customize_notification_body(self, db_picking):
        return re.sub("_",db_picking and db_picking.name or "",self.notification_body)

    @api.model
    def _send(self, to_data, partner_id=False, db_picking=False, max_limit=20):
        """
        to_data = dict(to or registration_ids)
        """
        if type(to_data)!=dict:
            return False
        if not to_data.get("to",False) and not to_data.get("registration_ids",False):
            if not partner_id:
                return False
            reg_data = self.env['delivery.boy.fcm.registered.devices'].sudo().search_read([('partner_id','=',partner_id)],limit=max_limit, fields=['token'])
            if not reg_data:
                return False
            to_data = {
                "registration_ids":[r['token'] for r in reg_data]
            }
        # notification = dict(title=self.notification_title, body=self.notification_body)
        notification = dict(id=random.randint(1, 99999), title=self._customize_notification_title(db_picking), body=self._customize_notification_body(db_picking), sound="default")
        if self.notification_color:
            notification['color'] = self.notification_color
        if self.notification_tag:
            notification['tag'] = self.notification_tag

        fcm_payload = dict(notification=notification)
        fcm_payload.update(to_data)
        data_message = dict(type="",id="",domain="",image="",name="")

        if self.banner_action == 'picking':
            data_message['type'] = 'picking'
        elif self.banner_action == 'invoice':
            data_message['type'] = 'invoice'
        else:
            data_message['type'] = 'none'
        data_message['image'] = _get_image_url(self._context.get('base_url'), 'delivery.boy.push.notification.template', self.id,'image_128', self.write_date.__str__())
        data_message['notificationId'] = random.randint(1, 99999)
        fcm_payload['data'] = data_message
        if partner_id:
            data = dict(
                   title=self._customize_notification_title(db_picking),
                   body=self._customize_notification_body(db_picking),
                   partner_id = partner_id,
                   banner=self.image, datatype='default'
                   )
        return self._pushMe(self._get_key(), json.dumps(fcm_payload).encode('utf8'), partner_id and data or False)

    name = fields.Char('Name', required=True, translate=True)
    notification_color = fields.Char('Color',default='PURPLE')
    notification_tag = fields.Char('Tag')
    notification_title = fields.Char('Title', required=True, translate=True)
    active = fields.Boolean(default=True, copy=False)
    notification_body = fields.Text('Body', translate=True)
    image = fields.Binary('Image', attachment=True)
    banner_action = fields.Selection([
        ('picking', 'Open Pickings Page'),
        ('invoice', 'Open Invoices Page'),
        ('none', 'Do nothing')],
        string='Action', required=True,
        default='none',
        help="Define what action will be triggerred when click/touch on the banner.")
    device_id = fields.Many2one('delivery.boy.fcm.registered.devices', string='Select Device')
    total_views = fields.Integer('Total # Views', default=0, readonly=1, copy=False)
    condition = fields.Selection([
        ('p_assigned', "Picking Assigned"),
        ('p_canceled', "Picking Canceled"),
        ('p_invoiced', "Picking Commission Invoiced"),
        ('p_paid', "Picking Commission Paid")
        ], string='Condition')

    # @api.multi
    def dry_run(self):
        self.ensure_one()
        to_data = dict(to=self.device_id and self.device_id.token or "")
        result = self._send(to_data, self.device_id and self.device_id.partner_id and self.device_id.partner_id.id or False)
        # raise UserError('Result: %r'%result)

    # @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s(copy)') % self.name)
        return super(DeliveryBoyPushNotificationTemplate, self).copy(default)


class DeliveryBoyPushNotification(models.Model):
    _name = 'delivery.boy.push.notification'
    _description = 'Delivery Boy Push Notification'
    _order = "activation_date, name"
    _inherit = ['delivery.boy.push.notification.template']


    @api.model
    def parse_n_push(self, max_limit=20, registration_ids=None):
        to_data = dict()
        if self.notification_type == 'token-auto':
            reg_data = self.env['delivery.boy.fcm.registered.devices'].sudo().search_read(limit=max_limit, fields=['token'])
            registration_ids = [r['token'] for r in reg_data]
        elif self.notification_type == 'token-manual':
            registration_ids = [d.token for d in self.device_ids]
        # elif self.notification_type == 'topic':
        #     to_data['to'] = '/topics/%s' % self.topic_id.name
        else:
            return [False,"Insufficient Data"]

        if registration_ids:
            if len(registration_ids) > 1:
                to_data['registration_ids'] = registration_ids
            else:
                to_data['to'] = registration_ids[0]
        return self._send(to_data)

    summary = fields.Text('Summary', readonly=True)
    activation_date = fields.Datetime('Activation Date', copy=False)
    notification_type = fields.Selection([
        ('token-auto', 'Token-Based(All Reg. Devices)'),
        ('token-manual', 'Token-Based(Selected Devices)'),
        # ('topic', 'Topic-Based'),
        ],
        string='Type', required=True,
        default='token-auto')
    # topic_id = fields.Many2one('fcm.registered.topics', string='Choose Topic')
    device_ids = fields.Many2many('delivery.boy.fcm.registered.devices', 'fcm_registered_devices_push_notif_rel',string='Choose Devices/Customers')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('hold', 'Hold'),
        ('error', 'Error'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    # @api.multi
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
        return True

    # @api.multi
    def action_confirm(self):
        for record in self:
            record.state = 'confirm'
        return True

    # @api.multi
    def action_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    # @api.multi
    def action_hold(self):
        for record in self:
            record.state = 'hold'
        return True

    # @api.multi
    def push_now(self):
        for record in self:
            response = record.parse_n_push()
            record.state = response and response[0] and 'done' or 'error'
            record.summary = response and response[1] or ''
        return True

    # @api.multi
    def duplicate_me(self):
        self.ensure_one()
        action = self.env.ref('delivery_boy.delivery_boy_push_notification_action').read()[0]
        action['views'] = [(self.env.ref('delivery_boy.delivery_boy_push_notification_view_form').id, 'form')]
        action['res_id'] = self.copy().id
        return action

class DeliveryBoyNotificationMessages(models.Model):
    _name = 'delivery.boy.notification.messages'
    _description = 'Delivery Boy Notification Messages'

    name = fields.Char('Message Name', default='/', index=True, copy=False, readonly=True)
    title = fields.Char('Title')
    subtitle = fields.Char('Subtitle')
    body = fields.Text('Body')
    # icon = fields.Binary('Icon')
    banner = fields.Binary('Banner')
    is_read = fields.Boolean('Is Read',default=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Delivery Boy", index=True, domain=[('is_delivery_boy','=', True)])
    active = fields.Boolean(default=True, readonly=True)
    # period = fields.Char('Period',compute='_compute_period')
    datatype = fields.Selection([
        ('default', 'Default'),
        ('order','Order')],
        string='Data Type', required=True,
        default='default',
        help="Notification Messages Data Type for your Delivery Boy App.")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('delivery.boy.notification.messages')
        return super(DeliveryBoyNotificationMessages,self).create(vals)

    # def _compute_period(self):
    #     for i in self:
    #         i.period = self.env['delivery.boy.config'].easy_date(i.create_date)

class DeliveryBoyFcmRegisteredDevices(models.Model):
    _name = 'delivery.boy.fcm.registered.devices'
    _description = 'All Registered Devices on FCM for Push Notifications.'
    _order = 'write_date desc'

    # @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.partner_id and record.partner_id.name or ''
            res.append((record.id, "%s(DeviceId:%s)"%(name,record.device_id)))
        return res

    name = fields.Char('Name')
    token = fields.Text('FCM Registration ID', readonly=True)
    device_id = fields.Char('Device Id', readonly=True)
    partner_id = fields.Many2one('res.partner', string="Delivery Boy", readonly=True, index=True)
    active = fields.Boolean(default=True, readonly=True)
    # write_date = fields.Datetime(string='Last Update', readonly=True, help="Date on which this entry is created.")
    description = fields.Text('Description', readonly=True)
