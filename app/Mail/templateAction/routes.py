from flask import request, redirect, url_for

from app import db
from app.Mail.templateAction import bp
from app.auth.decorators import auth_required
from app.models.TemplateMail import TemplateMail


@bp.route('/create', methods=['POST'])
@auth_required
def create():
    if request.method != 'POST':
        return 'Method not allowed', 405
    title_template = request.form['title_template']
    subject = request.form['subject_create']
    message = request.form['message_create']
    if not title_template or not subject or not message:
        return 'Missing parameters', 400
    newTemplate = TemplateMail(title_template=title_template, subject=subject, body=message)
    db.session.add(newTemplate)
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/delete/<string:templateName>', methods=['GET'])
@auth_required
def deleteTemp(templateName):
    if request.method != 'GET':
        return 'Method not allowed', 405
    template = TemplateMail.query.filter_by(title_template=templateName).first()
    if template is None:
        return 'Template not found', 404
    db.session.delete(template)
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/update', methods=['POST'])
@auth_required
def update():
    if request.method != 'POST':
        return 'Method not allowed', 405
    title_template = request.form['title_template']
    subject = request.form['subject_update']
    message = request.form['message_update']
    name = request.form['templateName']
    template = TemplateMail.query.filter_by(title_template=name).first()
    if template is None:
        return 'Template not found', 404
    template.title_template = title_template
    template.subject = subject
    template.body = message
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

