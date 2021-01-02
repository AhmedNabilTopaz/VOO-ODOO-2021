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

from odoo.http import request, Controller, route
from odoo import _
import json, werkzeug
from base64 import b64decode
from functools import wraps
from ast import literal_eval

class xml(object):

	@staticmethod
	def _encode_content(data):
		# .replace('&', '&amp;')
		return data.replace('<','&lt;').replace('>','&gt;').replace('"', '&quot;')

	@classmethod
	def dumps(cls, apiName, obj):
		_logger.warning("%r : %r"%(apiName, obj))
		if isinstance(obj, dict):
			return "".join("<%s>%s</%s>" % (key, cls.dumps(apiName, obj[key]), key) for key in obj)
		elif isinstance(obj, list):
			return "".join("<%s>%s</%s>" % ("I%s" % index, cls.dumps(apiName, element),"I%s" % index) for index,element in enumerate(obj))
		else:
			return "%s" % (xml._encode_content(obj.__str__()))

	@staticmethod
	def loads(string):
		def _node_to_dict(node):
			if node.text:
				return node.text
			else:
				return {child.tag: _node_to_dict(child) for child in node}
		root = ET.fromstring(string)
		return {root.tag: _node_to_dict(root)}

class DeliveryBoyServices(Controller):

	def _wrap2xml(self, apiName, data):
		resp_xml = "<?xml version='1.0' encoding='UTF-8'?>"
		resp_xml += '<odoo xmlns:xlink="http://www.w3.org/1999/xlink">'
		resp_xml += "<%s>"%apiName
		resp_xml += xml.dumps(apiName, data)
		resp_xml += "</%s>"%apiName
		resp_xml += '</odoo>'
		return resp_xml

	def _response(self, apiName, response, ctype='json'):
		if 'local' in response:
			response.pop("local")
		if ctype=='json':
			mime='application/json; charset=utf-8'
			body = json.dumps(response)
		else:
			mime='text/xml'
			body = self._wrap2xml(apiName,response)
		headers = [
					('Content-Type', mime),
					('Content-Length', len(body))
				]
		return werkzeug.wrappers.Response(body, headers=headers)

	def _checkProvidedData(self, neededData = set()):
		response = {}
		if  neededData - {key for key in self._mData}:
			response['responseCode'] = 400
			response['success'] = False
			response['message']= _('Insufficient Data Provided !!!')
		return response

	def __decorateMe(func):
		@wraps(func)
		def wrapped(inst, *args, **kwargs):
			inst._mData = request.httprequest.data and json.loads(request.httprequest.data.decode('utf-8')) or {}
			inst._mAuth = request.httprequest.authorization and (request.httprequest.authorization.get('password') or request.httprequest.authorization.get("username")) or None
			inst.base_url = request.httprequest.host_url
			inst._lcred = {}
			inst._sLogin = False
			inst.auth = True
			inst._mLang = request.httprequest.headers.get("lang") or None
			if request.httprequest.headers.get("Login"):
				try:
					inst._lcred = literal_eval(b64decode(request.httprequest.headers["Login"]).decode('utf-8'))
				except:
					inst._lcred = {"login":None,"pwd":None}
			elif request.httprequest.headers.get("SocialLogin"):
				inst._sLogin = True
				try:
					inst._lcred = literal_eval(b64decode(request.httprequest.headers["SocialLogin"]).decode('utf-8'))
				except:
					inst._lcred = {"authProvider":1,"authUserId":1234567890}
			else:
				inst.auth = False
			return func(inst, *args, **kwargs)
		return wrapped

	@__decorateMe
	def _authenticate(self, auth, **kwargs):
		if 'api_key' in kwargs:
			api_key  = kwargs.get('api_key')
		elif request.httprequest.authorization:
			api_key  = request.httprequest.authorization.get('password') or request.httprequest.authorization.get("username")
		else:
			api_key = False

		delivery_boy_config = request.env['delivery.boy.config'].sudo()
		response = delivery_boy_config._validate(api_key,{"lang":self._mLang})
		if not response.get('success'):
			return response
		context = response['local']
		context['base_url'] = self.base_url
		request.context =  dict(request.context, **context)
		if auth:
			result = delivery_boy_config.with_context(context).authenticate(self._lcred, kwargs.get('detailed',False),self._sLogin, context={'base_url':self.base_url})
			response.update(result)
		return response

	@route('/deliveryBoy/splashPageData', csrf=False, type='http',auth="public", methods=['GET','POST'])
	def getSplashPageData(self, **kwargs):
		response = self._authenticate(False, **kwargs)
		local = response.get('local')
		if response.get('success'):
			delivery_boy_config = request.env['delivery.boy.config'].sudo().search([],limit=1)
			if self.auth:
				result = delivery_boy_config.authenticate(self._lcred, True,self._sLogin, context={'base_url':self.base_url})
				response.update(result)
				self._tokenUpdate(partner_id=response.get('deliveryBoyPartnerId', False))
			result = delivery_boy_config.getDefaultData()
			response.update(result)
			response.update(self._languageData())
			response.pop('lang', None)
		return self._response('splashPageData', response)

	def _languageData(self):
		delivery_boy_config = request.env['delivery.boy.config'].sudo().search([], limit=1)
		temp = {
				'defaultLanguage':(delivery_boy_config.default_lang.code,delivery_boy_config.default_lang.name),
				'allLanguages':[(id.code,id.name) for id in delivery_boy_config.language_ids ]
		}

		return temp

	@route(['/deliveryBoy/pickings/<int:db_picking_id>', '/deliveryBoy/<int:partner_id>/pickings'], csrf=False, type='http', auth="public", methods=['GET','PUT','POST'])
	def deliveryBoyPickings(self,db_picking_id = False, partner_id = False ,**kwargs):
		response = self._authenticate(True, **kwargs)
		if response.get('success'):
			response['success'] = False
			response['responseCode'] = 400
			delivery_boy_config = request.env['delivery.boy.config'].sudo().search([],limit=1)
			try:
				if request.httprequest.method in ["GET"]:
					if partner_id:
						partner = request.env['res.partner'].sudo().browse(partner_id)
						try:
							partner.ensure_one()
							if partner.is_delivery_boy:
								response['totalCount'] = partner.picking_count
								response['deliveryBoyPickings']= delivery_boy_config.getDeliveryBoyPickings(
								partner_id,
								limit = kwargs.get('limit') and int(kwargs.get('limit')),
								offset = kwargs.get('offset') and int(kwargs.get('offset')),
								order = kwargs.get('order'),
								state = kwargs.get('state') and kwargs.get('state').split(','),
								picking_state_categorise = False
								)
								response['responseCode'] = 200
								response['message'] = _('Successfully retrieved the Pickings.')
								response['success'] = True
							else:
								raise Exception
						except Exception:
							response['message'] = _('Error. Invalid id.')
					else:
						result = delivery_boy_config.getDeliveryBoyPickings(db_picking_id = db_picking_id)
						result['responseCode'] = 200
						result['success'] = True
						result['message'] = _("Successfully retrieved the picking details")
						response.update(result)
				else:
					delivery_boy_picking = request.env['delivery.boy.pickings'].sudo().browse(db_picking_id)
					delivery_boy_picking.ensure_one()
					db_picking_state = delivery_boy_picking.picking_state
					if request.httprequest.method in ["PUT"]:
						available_states = ['denied','accept','delivered']
						if self._mData.get('state','') in available_states:
							if db_picking_state == 'accept' and self._mData.get('state') == 'delivered':
								if delivery_boy_config.verify_token:
									if delivery_boy_picking.delivery_token == self._mData.get('token',''):
										delivery_boy_picking.action_delivered()
									else:
										response['message'] = _("Invalid token provided!!!")
										return self._response('pickings', response)
								else:
									delivery_boy_picking.action_delivered()
							elif db_picking_state == 'assigned' and (self._mData.get('state') == 'accept' or self._mData.get('state') == 'denied'):
								delivery_boy_picking.picking_state = self._mData.get('state')
							else:
								response['message'] = _('Invalid picking state.')
								return self._response('pickings', response)

							response['message'] = _('Picking state successfully changed to %s')%(delivery_boy_picking.picking_state)
							response['responseCode'] = 200
							response['success'] = True
						else:
							response['message'] = _("Unidentified state!!!")
					else:
						if delivery_boy_picking.delivery_token == self._mData.get('token',''):
							response['message'] = _('Token is successfully verified')
							response['success'] = True
							response['responseCode'] = 200
						else:
							response['message'] = _('Invalid token provided!!!')
			except Exception as e:
				response['message'] = _('Picking not Found')

		return self._response('pickings', response)

	def _getInvoices(self, partner_id, **kwargs):
		result = []
		account_invoice = request.env['account.move'].sudo()
		for invoice in account_invoice.search([('partner_id','=',partner_id),('delivery_boy_invoice','=',True)], limit = kwargs.get('limit'), offset = kwargs.get('offset'), order = kwargs.get('order') or 'id desc'):
			invoice_details ={
			'id': invoice.id,
			'name': invoice.name or 'INV',
			'report': [],
			'invoiceDate': invoice.invoice_date.__str__() or '',
			'description': invoice.invoice_line_ids[0] and invoice.invoice_line_ids[0].name or '',
			'state': invoice.state,
			'amount': invoice.amount_total
			}
			for deliveryBoyPicking in invoice.delivery_boy_picking_ids:
				invoice_details['report'].append({
				'deliveryBoyPickingId': deliveryBoyPicking.id,
				'pickingState': deliveryBoyPicking.picking_state or '',
				'amount': deliveryBoyPicking.commission_amount or ''
				})
			result.append(invoice_details)
		return result

	@route('/deliveryBoy/<int:partner_id>/invoices', csrf=False, type='http', auth="none", methods=['GET'])
	def getDeliveryBoyInvoices(self, partner_id = False, **kwargs):
		response = self._authenticate(True, **kwargs)
		if response.get('success'):
			response['success'] = False
			partner = request.env['res.partner'].sudo().browse(partner_id)
			try:
				response['responseCode'] = 400
				partner.ensure_one()
				if partner.is_delivery_boy:
					response['invoices'] = self._getInvoices(
					partner_id,
					limit = kwargs.get('limit') and int(kwargs.get('limit')),
					offset = kwargs.get('offset') and int(kwargs.get('offset')),
					order = kwargs.get('order')
					)
					response['responseCode'] = 200
					response['message'] = _('Successfully retrieved the Invoices.')
					response['success'] = True
				else:
					raise Exception
			except Exception as e:
				response['message'] = str(" %r")%e

		return self._response('invoices', response)

	@route('/deliveryBoy/<int:partner_id>/dashboard', csrf=False, type='http', auth="none", methods=['GET'])
	def getDashboard(self, partner_id = False ,**kwargs):
		response = self._authenticate(True, **kwargs)

		if response.get('success'):
			partner = request.env['res.partner'].sudo().browse(partner_id)
			delivery_boy_config = request.env['delivery.boy.config'].sudo()
			response['success'] = False
			try:
				response['responseCode'] = 400
				partner.ensure_one()
				if partner.is_delivery_boy:
					response['totalPickings'] = partner.picking_count
					response['pickingDelivered'] = partner.picking_delivered
					response['deliveryBoyPickings'] = delivery_boy_config.getDeliveryBoyPickings(partner_id, state = kwargs.get('state') and kwargs.get('state').split(','))
					response['commissionInvoiced'] = partner.commission_invoiced
					response['commissionPaid'] = partner.commission_paid
					response['amountDue'] = partner.amount_due
					response['success'] = True
					response['responseCode'] = 200
					response['message'] = _('Successfully retrieved the dashboard data.')
				else:
					raise Exception
			except Exception as e:
				response['message'] = _('Error. Invalid id.')

		return self._response('dashboard', response)

	@route('/deliveryBoy/<int:partner_id>', csrf=False, type='http', auth="public", methods=['PUT'])
	def deliveryBoyStatus(self, partner_id = False, **kwargs):
		response = self._authenticate(True, **kwargs)

		if response.get('success'):
			response['success'] = False
			partner = request.env['res.partner'].sudo().browse(partner_id)
			try:
				response['responseCode'] = 400
				partner.ensure_one()
				if partner.is_delivery_boy:
					if self._mData.get('status') in [selection[0] for selection in partner._fields['delivery_boy_status'].selection]:
						active_pickings = request.env['delivery.boy.pickings'].sudo().search_count([('partner_id','=',partner_id),('picking_state','=','accept')])
						if active_pickings:
							response['message'] = _("Cannot change status\nStill having %s active picking%s")%(active_pickings,'s' if active_pickings > 1 else '')
							response['status'] = partner.delivery_boy_status
							return self._response('status', response)
						partner.delivery_boy_status =  self._mData.get('status')
						response['message'] = _('Status successfully changed to %s')%(partner.delivery_boy_status)
						response['status'] = partner.delivery_boy_status
						response['success'] = True
						response['responseCode'] = 200
					else:
						response['message'] = _("Unidentified status!!!")
				else:
					raise Exception
			except Exception:
				response['message'] = _("Error. Invalid id.")

		return self._response('status', response)

	@route('/deliveryBoy/login', csrf=False, type='http', auth="none", methods=['POST'])
	def login(self, **kwargs):
		kwargs['detailed'] = True
		response = self._authenticate(True, **kwargs)
		self._tokenUpdate(partner_id=response.get('deliveryBoyPartnerId'))
		return self._response('login', response)

	@route('/deliveryBoy/resetPassword', csrf=False, type='http', auth="none", methods=['POST'])
	def resetPassword(self, **kwargs):
		response = self._authenticate(False, **kwargs)
		if response.get('success'):
			delivery_boy_config = request.env['delivery.boy.config'].sudo()
			result = delivery_boy_config.resetPassword(self._mData.get('login',False))
			response.update(result)
		return self._response('resetPassword', response)

	@route('/deliveryBoy/logOut', csrf=False, type='http', auth="none", methods=['POST'])
	def signOut(self, **kwargs):
		response = self._authenticate(False, **kwargs)
		if response.get('success'):
			response['message'] = _("Have a Good Day !!!")
			self._tokenUpdate()
		return self._response('signOut', response)

	def _tokenUpdate(self, partner_id=False):
		FcmRegister = request.env['delivery.boy.fcm.registered.devices'].sudo()
		already_registered = FcmRegister.search([('device_id','=',self._mData.get("fcmDeviceId"))])
		if already_registered:
			already_registered.write({'token':partner_id and self._mData.get("fcmToken") or False,'partner_id':partner_id})
		else:
			FcmRegister.create({
				'token':self._mData.get("fcmToken",""),
				'device_id':self._mData.get("fcmDeviceId",""),
				'description':"%r"%self._mData,
				'partner_id':partner_id,
				})
		return True
