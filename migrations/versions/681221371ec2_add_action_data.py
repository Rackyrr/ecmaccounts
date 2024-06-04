"""add action data

Revision ID: 681221371ec2
Revises: b82487f94991
Create Date: 2024-06-04 10:21:30.628672

"""
from alembic import op
from app.models.Action import Action
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '681221371ec2'
down_revision = 'b82487f94991'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter des différentes actions dans la table action
    op.bulk_insert(Action.__table__,
                   [
                       {'action_id': 1, 'label': "Envoi mail",
                        'description': "Envoi d'un mail à un utilisateur."},

                       {'action_id': 2, 'label': "Supression compte",
                        'description': "Suppression d'un utilisateur."},

                       {'action_id': 3, 'label': "Garder le compte",
                        'description': "Le compte à été ajouté dans la liste des comptes à garder"},

                       {'action_id': 4, 'label': "Blocage compte",
                        'description': "Le compte à été vérouillé, il ne peut plus se connecter"},

                       {'action_id': 5, 'label': "Déblocage compte",
                        'description': "Le compte à été dévérouillé, il peut de nouveau se connecter"},

                       {'action_id': 6, 'label': "Envoi mail supression",
                        'description': "Un mail est envoyé au compte pour prévénir que ce dernier va être suprimé"},

                       {'action_id': 7, 'label': "Annulation supression",
                        'description': "Réaction du propriétaire du compte, annulation de la suppression du compte"}
                   ])


def downgrade():
    # Supprimer les actions de la table action
    op.execute("DELETE FROM action WHERE action_id IN (1, 2, 3, 4, 5, 6, 7)")
