from flask import render_template, request
from app.models.TemplateMail import TemplateMail
from app.Mail import bp


@bp.route('/write-mail', methods=['GET', 'POST'])
def writing():
    templates = TemplateMail.query.all()
    templatesReadModel = []
    for template in templates:
        templatesReadModel.append({
            'Nom template': template.title_template,
            'Sujet': template.subject,
            'Message': template.body
        })
    return render_template('send-mail.html', donnees=templatesReadModel)
