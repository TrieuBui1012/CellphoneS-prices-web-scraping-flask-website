from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from werkzeug.exceptions import abort

from flaskr.db import get_db

import flaskr.web_scraping as webscrap

import requests, bs4, re, os

from selenium import webdriver
from selenium.webdriver.common.by import By

bp = Blueprint('price', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    id = request.args.get('id', default=-1, type=int)
    db = get_db()
    devices = db.execute(
        'SELECT *'
        ' FROM device'
        ' ORDER BY device_name'
    ).fetchall()

    if request.method == 'POST':
        device_input = request.form['add-device-input']  
        result = webscrap.get_data_from_device_input_by_selenium(device_input)
        if result['error'] is not None:
            flash(result['error'])
        else:
            isExisted = False
            for device in devices:
                if device['device_name'] == result['device_name']: isExisted = True
            if isExisted == False:
                db.execute(
                    'INSERT INTO device (device_name, device_img)'
                    ' VALUES (?, ?)',
                    (result['device_name'], result['device_img'])
                )
                db.commit()
                device_id = db.execute(
                    'SELECT id'
                    ' FROM device'
                    ' WHERE device_name = ?',
                    (result['device_name'],)
                ).fetchone()
                db.execute(
                    'INSERT INTO price (price, device_id)'
                    ' VALUES (?, ?)',
                    (result['price'], device_id['id'])
                )
                db.commit()
            else: flash('This device has already added.')
        return redirect(url_for('price.index'))
    
    if id == -1:
        return render_template('price/index.html', devices=devices)
    else:
        prices = db.execute(
            'SELECT *'
            ' FROM price'
            ' WHERE device_id = ?'
            ' ORDER BY created DESC',
            (id,)
        ).fetchall()
        device = db.execute(
            'SELECT *'
            ' FROM device'
            ' WHERE id = ?',
            (id,)
        ).fetchone()
        return render_template('price/index.html', devices=devices, prices=prices, device=device)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    db = get_db()
    db.execute('DELETE FROM price WHERE device_id = ?', (id,))
    db.commit()
    try:
        device_img = db.execute(
            'SELECT device_img'
            ' FROM device'
            ' WHERE id = ?',
            (id,)
        ).fetchone()
    except:
        pass
    os.remove(os.path.join(current_app.root_path, 'static', os.path.basename(device_img['device_img'])))
    db.execute('DELETE FROM device WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('price.index'))

@bp.route('/scrap-price', methods=('POST',))
def scrap_price():
    db = get_db()
    selected_names = request.form.getlist('devices-scraping')

    for name in selected_names:
        result = webscrap.get_data_from_device_input_by_selenium(name)
        if result['error'] is not None:
            flash(result['error'])
        else:
            device_id = db.execute(
                'SELECT id'
                ' FROM device'
                ' WHERE device_name = ?',
                (result['device_name'],)
            ).fetchone()
            db.execute(
                'INSERT INTO price (price, device_id)'
                ' VALUES (?, ?)',
                (result['price'], device_id['id'])
            )
            db.commit()

    return redirect(url_for('price.index'))