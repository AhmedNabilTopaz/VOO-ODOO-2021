# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import models
from odoo.tools.misc import clean_context

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def getTrackDetails(self, vals):
        trackFields = self.getTrackingFields()
        tracked_fields = vals.keys()
        tracked_fields = list(set(tracked_fields) - set(trackFields))
        track_self = self.with_lang()
        trackVals = self.fields_get(tracked_fields)
        initial_values = dict((record.id, dict((key, getattr(record, key)) for key in trackVals))
                                  for record in track_self)
        return {'trackVals':trackVals, 'initial_values':initial_values}

    def addTrackingMsg(self, data):
        track_self = self.with_lang()
        trackVals, initial_values = data.get('trackVals'), data.get('initial_values')
        if trackVals:
            tracking = track_self.with_context(clean_context(self._context)).message_track(trackVals, initial_values)
            if any(change for rec_id, (change, tracking_value_ids) in tracking.items()):
                (changes, tracking_value_ids) = tracking[track_self[0].id]
                track_self._message_track_post_template(changes)
        return True

    def getTrackingFields(self):
        tracked_fields = []
        for name, field in self._fields.items():
            tracking = getattr(field, 'tracking', None) or getattr(field, 'track_visibility', None)
            if tracking:
                tracked_fields.append(name)
        return tracked_fields