from flask import current_app
from ldap3 import Server, ALL, Connection


class Ldap:
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
        :return:
        """
        server = Server(current_app.config['LDAP_SERVER'], get_info=ALL)
        return Connection(server, user=current_app.config['LDAP_USER'], password=current_app.config['LDAP_PASSWORD'],
                          check_names=True)

    def closeConnection(self):
        """
        Fermer la connexion LDAP
        """
        self.connection.unbind()

    def getUserMail(self, login):
        """
        Recuperer l'email d'un utilisateur par le login
        :param login:
        :return:
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(&(objectclass=supannPerson)(uid=' + login + '))',
                        attributes=['mailLocalAddress'], search_scope='SUBTREE')
            if len(conn.response) == 0:
                return None
            return conn.response[0]['attributes']['mailLocalAddress'][0]

    def getAllUserMail(self):
        """
        Recuperer l'email de tous les utilisateurs
        :return:
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(objectclass=supannPerson)',
                        attributes=['uid', 'mailLocalAddress'], search_scope='SUBTREE')
            AccountsMail = {}
            for entry in conn.response:
                email = entry['attributes'].get('mailLocalAddress', '')
                if email:
                    AccountsMail[entry['attributes']['uid'][0]] = email[0]
                else:
                    AccountsMail[entry['attributes']['uid'][0]] = 'Non renseigné'
            return AccountsMail

    def getUserByLogin(self, login):
        """
        Recuperer un utilisateur par le login
        :param login:
        :return:
        """
        with self.connection as conn:
            conn.search(current_app.config['LDAP_SEARCH_BASE'], '(&(objectclass=supannPerson)(uid=' + login + '))',
                        attributes=['uid', 'mailLocalAddress'],
                        search_scope='SUBTREE')
            if len(conn.response) == 0:
                return None
            return {"login": conn.response[0]['attributes']['uid'][0],
                    "email": conn.response[0]['attributes']['mailLocalAddress'][0]}
