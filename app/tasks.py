import time

import sys

import gspread

from datetime import datetime

from flask import jsonify

from oauth2client.service_account import ServiceAccountCredentials

from rq import get_current_job

from app import db

from app.models import Task, Order

from app import create_app

app = create_app()
app.app_context().push()


def _set_task_progress(progress, result=None):
    """This generates a notificaiton entry in 
    the db in order to track the progress of 
    a process.
    """
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification(
            'task_progress', {
                'task_id': job.get_id(),
                'progress': progress
                }
            )
        if progress >= 100:
            task.user.add_notification(
                'task_progress', {
                'task_id': job.get_id(),
                'progress': progress,
                'result': result
                }
                )
            task.complete = True
            time.sleep(5)
            tasks = Task.query.all()
            for task in tasks:
                print(task)
                db.session.delete(task)
                db.session.commit()
        db.session.commit()

 
def export_report(users, products, to, frm):
    """This tries to run the report generation function and logs
    an error if it is unable to do so.
    """
    try:
        _set_task_progress(0)
        complete = False
        while not complete:
            complete = generate_async_report(users, products, to, frm)
        _set_task_progress(100, complete)
    except Exception:
        _set_task_progress(100, "Error when exporting")
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


def generate_async_report(users, products, to, frm):
    """This generates a report in the form of 
    a google sheet which is then shared with the 
    shop google account.
    """
    scope = [
        'https://spreadsheets.google.com/feeds', 
        'https://www.googleapis.com/auth/drive'
        ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'app/static/js/client_secret.json', 
        scope
        )
    client = gspread.authorize(creds)
    sheet = client.create(
        f"Report Results {datetime.utcnow().strftime('%d-%m-%y-%H-%-M')}"
        )
    worksheet = sheet.sheet1
    worksheet.update_cell(1, 1, "Email")
    worksheet.update_cell(1, 2, "Product")
    worksheet.update_cell(1, 3, "Date")
    worksheet.update_cell(1, 4, "Quantity")
    row = 1
    for i, user in enumerate(users):
        for product in products:
            order = Order.query.join().filter_by(
                user_id=user.id, 
                product_id=product.id
                ).first()
            if order and (not to or not frm):
                row = sheet_update(
                    row, 
                    order.buyer.email, 
                    order.product.item, 
                    order.timestamp, 
                    order.qty, 
                    worksheet, 
                    sheet
                    )
            elif (order and 
                frm <= order.timestamp.date() and 
                to >= order.timestamp.date()):
                row = sheet_update(
                    row, 
                    order.buyer.email, 
                    order.product.item, 
                    order.timestamp, 
                    order.qty, 
                    worksheet, 
                    sheet
                    )
            _set_task_progress(100 * i//len(users))
            print(100 * i//len(users))
    if row > 1:
        sheet.share(
            app.config['ADMINS'], 
            perm_type='user', 
            role='writer'
            )
        return "Export complete"
    else:
        return "No results"


def sheet_update(row, buyer, product, timestamp, qty, worksheet, sheet):
    """This updates a row in the report spreadsheet with email, 
    product bought, quantity and date/time of sale.
    """
    row += 1
    worksheet.update_cell(row, 1, buyer)
    worksheet.update_cell(row, 2, product)
    worksheet.update_cell(row, 3, timestamp.strftime('%d-%m-%y'))
    worksheet.update_cell(row, 4, qty)
    sheetId = worksheet._properties['sheetId']
    body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                        "startIndex": 0,  
                        "endIndex": 4  
                    }
                }
            }
        ]
    }
    sheet.batch_update(body)
    return row