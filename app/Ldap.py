from datetime import datetime, timedelta

from flask import current_app
from ldap3 import Server, ALL, Connection


class Ldap:
    """
    Classe pour la connexion à l'annuaire LDAP
    Fournir les informations de connexion dans un fichier de configuration
    """

    _instance = None

    def __new__(cls):
        """
        Singleton pour la connexion LDAP
        """
        if not cls._instance:
            cls._instance = super(Ldap, cls).__new__(cls)
            cls._instance.connection = cls._instance.connect()
        return cls._instance

    def connect(self):
        """
        Connecter à l'annuaire LDAP
        :return: Connection ldap3
        """
        server = Server(current_app.config['LDAP_SERVER'], get_info=ALL)
        return Connection(server, user=current_app.config['LDAP_USER'], password=current_app.config['LDAP_PASSWORD'],
                          check_names=True)

    def closeConnection(self):
        """
        Fermer la connexion LDAP
        """
        self.connection.unbind()

    def getAllUsersBasicInfo(self):
        """
        Recuperer les informations de base de tous les utilisateurs
        (login, email, groupe)
        :return: Liste de Dictionnaires (login, email, groupe)
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(objectclass=supannPerson)',
                        attributes=['uid', 'uidNumber', 'mailLocalAddress', 'supannAffectation'],
                        search_scope='SUBTREE')
            AccountsMail = {}
            for entry in conn.response:
                email = entry['attributes'].get('mailLocalAddress', '')
                groupe = entry['attributes'].get('supannAffectation', '')
                uidNumber = entry['attributes'].get('uidNumber', '')
                if email:
                    email = email[0]
                else:
                    email = 'Non renseigné'
                if groupe:
                    if len(groupe) > 1:
                        groupe = ", ".join(groupe)
                    else:
                        groupe = groupe[0]
                else:
                    groupe = 'Non renseigné'
                AccountsMail[entry['attributes']['uid'][0]] = {'email': email, 'groupe': groupe,
                                                               'uidNumber': uidNumber}
            return AccountsMail

    def getUserByLogin(self, login):
        """
        Recuperer un utilisateur par le login
        :param login:
        :return: Dictionnaire (login, email, groupe)
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(&(objectclass=supannPerson)(uid=' + login + '))',
                        attributes=['uid', 'uidNumber', 'mailLocalAddress', 'supannAffectation'],
                        search_scope='SUBTREE')
            if len(conn.response) == 0:
                return None
            email = conn.response[0]['attributes'].get('mailLocalAddress', '')
            groupe = conn.response[0]['attributes'].get('supannAffectation', '')
            uidNumber = conn.response[0]['attributes'].get('uidNumber', '')
            if email:
                email = email[0]
            else:
                email = 'Non renseigné'
            if groupe:
                if len(groupe) > 1:
                    groupe = ", ".join(groupe)
                elif len(groupe) == 1:
                    groupe = groupe[0]
                else:
                    groupe = 'Non renseigné'
            return {"login": conn.response[0]['attributes']['uid'][0],
                    "email": email,
                    "groupe": groupe,
                    "uidNumber": uidNumber}

    def seeUserExample(self):
        """
        Exemple de recherche d'un utilisateur pour voir les attributs
        :return:
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(&(objectclass=supannPerson)(uid=moi2006))',
                        attributes=['*'], search_scope='SUBTREE')
            return str(conn.response[0])

    def getUsersWithPwdLastSetOver(self, days):
        """
        Recuperer les utilisateurs dont le mot de passe a été modifié il y a plus de x jours
        :param days:unix timestamp
        :return: liste des utilisateurs correspondants à la recherche (login, email, groupe, pwdChangedTime)
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(objectclass=supannPerson)',
                        attributes=['uid', 'mailLocalAddress', 'supannAffectation', 'sambaPwdLastSet'],
                        search_scope='SUBTREE')
            Accounts = []
            for entry in conn.response:
                pwdChangedTime = entry['attributes'].get('sambaPwdLastSet', '')
                email = entry['attributes'].get('mailLocalAddress', '')
                groupe = entry['attributes'].get('supannAffectation', '')
                if email:
                    email = email[0]
                else:
                    email = 'Non renseigné'
                if groupe:
                    if len(groupe) > 1:
                        groupe = ", ".join(groupe)
                    else:
                        groupe = groupe[0]
                else:
                    groupe = 'Non renseigné'
                if pwdChangedTime:
                    pwdChangedTime = datetime.fromtimestamp(pwdChangedTime)
                    if (datetime.now() - pwdChangedTime) >= timedelta(days=days):
                        Accounts.append({'login': entry['attributes']['uid'][0], 'email': email, 'groupe': groupe,
                                         'pwdChangedTime': pwdChangedTime, 'NeverChanged': False})
                else:
                    Accounts.append({'login': entry['attributes']['uid'][0], 'email': email, 'groupe': groupe,
                                     'pwdChangedTime': '', 'NeverChanged': True})
            return Accounts
