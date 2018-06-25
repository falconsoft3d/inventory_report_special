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

class WizardReportStockMinimum(models.TransientModel):
    _name = "wizard.report.stock.minimum"
    _description = "Reporte de Stock Minimo"
    
    
    warehouse_option = fields.Selection([('1', 'Todos los Almacenes' ),("2","Almacen Específico")],'Mostrar: ', default = '1' ,required = True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Almacen')
    
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
        
        products_ids = self.env['product.product'].search([('active', '=', True)])
        for p in products_ids:
            obj_products_warehouse_orderpoint_id= self.env['stock.warehouse.orderpoint'].search([('product_id', '=', p.id)])
            if obj_products_warehouse_orderpoint_id:
                print "obj_products_warehouse_orderpoint_id.product_min_qty>>>>>>>>>>>>",obj_products_warehouse_orderpoint_id.product_min_qty
                min_qty = obj_products_warehouse_orderpoint_id.product_min_qty
                print "p.name>>",p.name
                print "min_qty>>",min_qty
                print "p.qty_available>>",p.qty_available
                lis = p.property_stock_procurement.complete_name.split('/')
                warehouse_code = lis[1]
                print "lis>>>11>>>>>",lis[1]
                warehouse_id = self.env['stock.warehouse'].search([('code', '=', warehouse_code)])
                print "warehouse_id>>>",warehouse_id
                print "lis>>>22>>>>>",lis[1]
                print "producto.property_stock_procurement.location_id>>",p.property_stock_procurement.location_id
                print "producto.property_stock_procurement.location_id.name>>",p.property_stock_procurement.location_id
                
                name_aux = p.name
                if p.attribute_line_ids:
                    for a in p.attribute_line_ids:
                        name_aux = name_aux +"-"+a.display_name
                if p.attribute_value_ids:
                    for b in p.attribute_value_ids:
                        name_aux = name_aux +"-"+b.name
                vals = {
                    'name': ' '+name_aux,
                    'product_id': p.id,
                    'qty':p.qty_available,
                    'qty_minimum':min_qty,
                    'warehouse_id':warehouse_id.name or "",
                    'location_id':p.property_stock_procurement.location_id.name or "",
                }
                print "vals>>", vals
                if min_qty >= p.qty_available:
                    print "PRODUCTO VALIDO"
                    if (self.warehouse_option == '2' and self.warehouse_id.id == warehouse_id.id) or self.warehouse_option == '1':
                        lines_total.append(vals)
        path = '/tmp/file_%s.csv'% (datetime.today().strftime("%d-%m-%Y"))
        fp = StringIO()
        with open(path, 'w') as csvfile:
            csvfile.write("Reporte de; Stock ;Minimo;\n")
            csvfile.write("Fecha:;{1} \n".format("",datetime.today().strftime("%d-%m-%Y") ))
            csvfile.write("Id Producto;Producto;Cantidad del Producto; Cantidad Minima; Almacen; Locacion \n")
            
            for lin in lines_total:
                csvfile.write("{0};{1};{2};{3};{4};{5} \n".format(lin['product_id'], lin['name'], lin['qty'], lin['qty_minimum'], lin['warehouse_id'], lin['location_id']))
        
        fp.close()
        csvfile.close()
        arch = open(path, 'r').read()
        data = base64.encodestring(arch)
        attach_vals = {
                        'name':'Reporte de Stock Minimo %s.csv' % (datetime.today().strftime("%d-%m-%Y")),
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
    
    
    
