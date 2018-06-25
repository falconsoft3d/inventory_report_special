# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
import tempfile
import shutil
import base64
import os
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import dicttoxml
import  sys
import xmltodict
from lxml import etree
import locale
import time
from odoo import osv
from datetime import datetime, date, time, timedelta
from odoo import api, fields, models
import csv
import StringIO
from odoo import http
import unicodedata
try:
    import xlwt
except ImportError:
    xlwt = None
import re
from cStringIO import StringIO

class WizardReportProductsRotation(models.TransientModel):
    _name = "wizard.report.products.rotation"
    _description = "Reporte de Rotacion de Productos"
    
    
    date_init = fields.Date('Fecha Inicio', required=True,  default=lambda self: datetime.today())
    date_end = fields.Date( 'Fecha Fin', required=True,  default=lambda self: datetime.today())
    company_id = fields.Many2one('res.company', 'Company',  default=lambda self: self.env.user.company_id)
    report_option = fields.Selection([('1', 'Compras' ),("2","Ventas")],'Mostrar: ', default = '1' ,required = True)
    products_without_rotation_view = fields.Boolean('Mostrar Productos sin Movimientos', default = True)
    
    @api.multi
    def get_csv(self,data):
        print "INICIO PROCESO WIZARD CSV"
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        print "self>",self
        print "context>",context
        print "active_id>",active_id
        print "data>",data
        
        context = dict(self._context or {})
        active_ids = data.get('active_ids', False)
        lines_total = []
        
        productsx_ids = self.env['product.product'].search([('active', '=', True)])
        for p in productsx_ids:
            print "p.name>>",p.name
            if p.attribute_line_ids:
                for a in p.attribute_line_ids:
                    print "a.display_name>>",a.display_name
            if p.attribute_value_ids:
                for b in p.attribute_value_ids:
                    print "b.display_name>>",b.name
        
        
        if self.report_option == '1':
            print "+++++++++++1111+++++++++++++"
            products_ids = self.env['product.product'].search([('active', '=', True)])
            for p in products_ids:
                qty_sale = 0
                print "p.name>>",p.name
                invoice_ids = self.env['account.invoice'].search([('date','>=', self.date_init), ('date','<=', self.date_end), ('type','=', 'in_invoice')])
                
                print "+++++++++++11AA11+++++++++++++"
                for invoice in invoice_ids:
                    
                    print "invoice.name>>",invoice.id
                    for line in invoice.invoice_line_ids:
                        if line.product_id.id == p.id:
                            
                            print "line.product_id>>",line.product_id.id
                            print "line.quantity>>",line.quantity
                            qty_sale += line.quantity
                print "qty_sale>>",qty_sale
                if qty_sale != 0:
                    name_aux = p.name
                    print "p.name>>",p.name
                    
                    if p.attribute_line_ids:
                        for a in p.attribute_line_ids:
                            print "a.display_name>>",a.display_name
                            name_aux = name_aux +"-"+a.display_name
                    if p.attribute_value_ids:
                        for b in p.attribute_value_ids:
                            print "b.display_name>>",b.name
                            name_aux = name_aux +"-"+b.name
                    
                    vals = {
                        'product_id':p.id, 
                        'name':name_aux, 
                        'category':p.categ_id.name or "", 
                        'uom':p.product_tmpl_id.uom_id.name or "", 
                        'qty_sale':qty_sale,
                    }
                    print "vals>>",vals
                    lines_total.append(vals)
                elif qty_sale == 0 and self.products_without_rotation_view:
                    name_aux = p.name
                    print "p.name>>",p.name
                    
                    if p.attribute_line_ids:
                        for a in p.attribute_line_ids:
                            print "a.display_name>>",a.display_name
                            name_aux = name_aux +"-"+a.display_name
                    if p.attribute_value_ids:
                        for b in p.attribute_value_ids:
                            print "b.display_name>>",b.name
                            name_aux = name_aux +"-"+b.name
                    
                    vals = {
                        'product_id':p.id, 
                        'name':name_aux, 
                        'category':p.categ_id.name, 
                        'uom':p.product_tmpl_id.uom_id.name, 
                        'qty_sale':0.0,
                    }
                    print "vals>>",vals
                    lines_total.append(vals)
                    
                print "+++++++++++22AA22+++++++++++++"
                
            print "+++++++++++22222+++++++++++++"
            
            
            
            
            print "Lines_total>>",lines_total
            
            for numPasada in range(len(lines_total)-1,0,-1):
                for i in range(numPasada):
                    if lines_total[i]['qty_sale']<lines_total[i+1]['qty_sale']:
                        temp = lines_total[i]
                        lines_total[i] = lines_total[i+1]
                        lines_total[i+1] = temp
            print "lines_total>>",lines_total
            path = '/tmp/file_%s.csv'% (datetime.today().strftime("%d-%m-%Y"))
            fp = StringIO()
            with open(path, 'w') as csvfile:
                csvfile.write("Reporte de; Rotacion de;Productos;\n")
                csvfile.write("Fecha Inicio:;{1};Fecha Fin;{3} \n".format("",self.date_init,"", self.date_init))
                csvfile.write("Id Producto;Producto;Categoria; UM; Cantidad Comprada \n")
                
                for lin in lines_total:
                    csvfile.write("{0};{1};{2};{3};{4} \n".format(lin['product_id'], lin['name'], lin['category'], lin['uom'], lin['qty_sale']))
            
            fp.close()
            csvfile.close()
            arch = open(path, 'r').read()
            data = base64.encodestring(arch)
            attach_vals = {
                            'name':'Reporte de Rotacion de Productos %s.csv' % (datetime.today().strftime("%d-%m-%Y")),
                            'datas':data,
                            'datas_fname':'File#_%s.csv' % (datetime.today().strftime("%d-%m-%Y")),
            }
            doc_id = self.env['ir.attachment'].create(attach_vals)
            return {
                    'type' : "ir.actions.act_url",
                    'url': "web/content/?model=ir.attachment&id="+str(doc_id.id)+"&filename_field=datas_fname&field=datas&download=true&filename="+str(doc_id.name),
                    'target': "self",
            }
        
        
        
        if self.report_option == '2':
            print "+++++++++++1111+++++++++++++"
            products_ids = self.env['product.product'].search([('active', '=', True)])
            for p in products_ids:
                qty_sale = 0
                print "p.name>>",p.name
                invoice_ids = self.env['account.invoice'].search([('date','>=', self.date_init), ('date','<=', self.date_end), ('type','=', 'out_invoice')])
                
                print "+++++++++++11AA11+++++++++++++"
                for invoice in invoice_ids:
                    
                    print "invoice.name>>",invoice.id
                    for line in invoice.invoice_line_ids:
                        if line.product_id.id == p.id:
                            
                            print "line.product_id>>",line.product_id.id
                            print "line.quantity>>",line.quantity
                            qty_sale += line.quantity
                print "qty_sale>>",qty_sale
                if qty_sale != 0:
                    name_aux = p.name
                    print "p.name>>",p.name
                    if p.attribute_line_ids:
                        for a in p.attribute_line_ids:
                            print "a.display_name>>",a.display_name
                            name_aux = name_aux +"-"+a.display_name
                    if p.attribute_value_ids:
                        for b in p.attribute_value_ids:
                            print "b.display_name>>",b.name
                            name_aux = name_aux +"-"+b.name
                    vals = {
                        'product_id':p.id, 
                        'name':name_aux, 
                        'category':p.categ_id.name, 
                        'uom':p.product_tmpl_id.uom_id.name, 
                        'qty_sale':qty_sale,
                    }
                    print "vals>>",vals
                    lines_total.append(vals)
                if qty_sale == 0 and self.products_without_rotation_view:
                    name_aux = p.name
                    print "p.name>>",p.name
                    
                    if p.attribute_line_ids:
                        for a in p.attribute_line_ids:
                            print "a.display_name>>",a.display_name
                            name_aux = name_aux +"-"+a.display_name
                    if p.attribute_value_ids:
                        for b in p.attribute_value_ids:
                            print "b.display_name>>",b.name
                            name_aux = name_aux +"-"+b.name
                    
                    vals = {
                        'product_id':p.id, 
                        'name':name_aux, 
                        'category':p.categ_id.name, 
                        'uom':p.product_tmpl_id.uom_id.name, 
                        'qty_sale':0.0,
                    }
                    print "vals>>",vals
                    lines_total.append(vals)
                
                print "+++++++++++22AA22+++++++++++++"
                
            print "+++++++++++22222+++++++++++++"
            
            print "Lines_total>>",lines_total
            
            for numPasada in range(len(lines_total)-1,0,-1):
                for i in range(numPasada):
                    if lines_total[i]['qty_sale']<lines_total[i+1]['qty_sale']:
                        temp = lines_total[i]
                        lines_total[i] = lines_total[i+1]
                        lines_total[i+1] = temp
            print "lines_total>>",lines_total
            path = '/tmp/file_%s.csv'% (datetime.today().strftime("%d-%m-%Y"))
            fp = StringIO()
            with open(path, 'w') as csvfile:
                csvfile.write("Reporte de; Rotacion de;Productos;\n")
                csvfile.write("Fecha Inicio:;{1};Fecha Fin;{3} \n".format("",self.date_init,"", self.date_init))
                csvfile.write("Id Producto;Producto;Categoria; UM; Cantidad Vendida \n")
                
                for lin in lines_total:
                    csvfile.write("{0};{1};{2};{3};{4} \n".format(lin['product_id'], lin['name'], lin['category'], lin['uom'], lin['qty_sale']))
            
            fp.close()
            csvfile.close()
            arch = open(path, 'r').read()
            data = base64.encodestring(arch)
            attach_vals = {
                            'name':'Reporte de Rotacion de Productos %s.csv' % (datetime.today().strftime("%d-%m-%Y")),
                            'datas':data,
                            'datas_fname':'File#_%s.csv' % (datetime.today().strftime("%d-%m-%Y")),
            }
            doc_id = self.env['ir.attachment'].create(attach_vals)
            return {
                    'type' : "ir.actions.act_url",
                    'url': "web/content/?model=ir.attachment&id="+str(doc_id.id)+"&filename_field=datas_fname&field=datas&download=true&filename="+str(doc_id.name),
                    'target': "self",
            }
        
        return True
    
    
