from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from flask_login import login_required
from bd import conectar_bd

admin_accesibilidad = Blueprint('admin_accesibilidad', __name__)

@admin_accesibilidad.route('/admin/accesibilidad')
@login_required
def gestion_accesibilidad():
    if session.get('usuario_tipo') != 'admin':
        flash("Acceso denegado", "error")
        return redirect(url_for('inicio.inicio'))
    
    return render_template('admin_accesibilidad.html')