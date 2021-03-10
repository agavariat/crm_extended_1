from odoo import fields,models,api,SUPERUSER_ID
import datetime

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lost_start_date = fields.Datetime(string="StartDate")
    lost_end_date = fields.Datetime(string="EndDate")
    score = fields.Char(string="Score")
    stage_name = fields.Char(string="stage name",related="stage_id.name")
    teacher_id = fields.Many2one('res.users',related="team_id.user_id",string="teacher")
    x_motivo = fields.Char(string="Motivo")
    # facilitador = fields.Many2one('res.users',string="Facilitador",compute="_compute_facilitador")

    # def _compute_facilitador(self):
    #     for line in self:
    #         team_id = self.env['crm.team'].search([('user_id','=',self.env.uid)])
    #         line.facilitador = team_id.user_id.id

class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    def _default_crm_lead_date(self):
        lead_id = self.env['crm.lead'].search([('id','=',self._context.get('default_lead_id'))])
        if lead_id:
            return lead_id.date_open
        else:
            return datetime.datetime.now().date()

    start_date = fields.Date(string="StartDate" ,default=_default_crm_lead_date)
    end_date = fields.Date(string="EndDate",default=fields.Datetime.now)
    score = fields.Selection([('p_good','Muy Bueno'),('good','Bueno'),('bad','Malo'),('p_bad','Muy Malo')],string="Puntaje",default="Muy Bueno")
    x_motivo = fields.Char(string="Motivo")

    def action_lost_reason_apply(self):
        res = super(CrmLeadLost, self).action_lost_reason_apply()
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads.lost_start_date = self.start_date
        leads.lost_end_date = self.end_date
        leads.score = self.score
        leads.x_motivo = self.x_motivo
        return res

class salesTeam(models.Model):
    _inherit = 'crm.team'

    def write(self,vals):
        if vals and vals.get('member_ids'):
            for member in vals.get('member_ids'):
                if member[0] == 3:
                    crm_ids = self.env['crm.lead'].search([('user_id','=',member[1])])
                    for crm_id in crm_ids:
                        crm_id.team_id = False
                if member[0] == 6:
                    crm_ids = self.env['crm.lead'].search([('user_id', 'in', member[2]),('team_id','=',False)])
                    for crm_id in crm_ids:
                        crm_id.team_id = self.id
        return super(salesTeam, self).write(vals)
