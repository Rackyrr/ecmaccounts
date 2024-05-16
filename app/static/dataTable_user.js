let table = new DataTable('#myTable', {
    //Selection des lignes possibles
    select: true,
    responsive: true,
    //Langue du tableau
    language: {
        url: 'https:////cdn.datatables.net/plug-ins/2.0.5/i18n/fr-FR.json',
        paginate : {
            first: '«',
            previous: '‹',
            next: '›',
            last: '»'
        },
        select: {
            columns : "",
            cells : "",
        }
    },
    layout:{
        top2: 'searchBuilder', //SearchBuilder en haut à gauche
        topEnd: {
            buttons: [ //Boutons selectionner tout et deselectionner tout
                {
                    text : "Selectionner tout",
                    extend: 'selectAll',
                    selectorModifier: {
                        search : 'applied',
                    }
                },
                {
                    text : "Deselectionner tout",
                    extend: 'selectNone',
                    selectorModifier: {
                        search : 'applied',
                    }
                }
            ]
        },
        bottom:{
            buttons: [ //Boutons d'actions
                {
                    text: 'Supprimer',
                    action: function (e, dt, node, config, cb) {
                        // On récupère les lignes sélectionnées dans le tableau (en bleu)
                        const selectedRows = dt.rows({ selected: true });
                        // Pour supprimer, il faut au moins une ligne sélectionnée
                        if (selectedRows.count() > 0) {
                            let selectedLogin = [];
                            // On récupère le login de chaque ligne sélectionnée
                            selectedRows.every(function () {
                                selectedLogin.push(this.data()[0]);
                            });
                            $('#deleteListLogin').val(selectedLogin.join(',')); // On met les logins dans le champ caché du form
                            $('#deleteModal').modal('show'); // On affiche la modal pour obtenir la raison et confirmer
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    },
                    className: 'btn-danger'
                },
                {
                    text: 'Annuler suppression',
                    action: function (e, dt, node, config, cb) {
                        const selectedRows = dt.rows({ selected: true });
                        if (selectedRows.count() > 0) {
                            let loginList = [];
                            selectedRows.every(function () {
                                loginList.push(this.data()[0]);
                            });
                            $('#cancelDeleteListLogin').val(loginList.join(','));
                            $('#cancelDeleteModal').modal('show');
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    }
                },
                {
                    text:'Envoyer un mail',
                    action: function (e, dt, node, config, cb) {
                        const selectedRows = dt.rows({ selected: true });
                        if (selectedRows.count() > 0) {
                            let mailList = [];
                            //Affiche chaque ligne sélectionné dans la console
                            selectedRows.every(function () {
                                mailList.push(this.data()[1]);
                            });
                            $('#listMail').val(mailList.join(','));
                            $('#sendMailList').submit()
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    }
                },
                {
                    text:'Garder le(s) compte(s)',
                    action: function (e, dt, node, config, cb) {
                        // On récupère les lignes sélectionnées dans le tableau (en bleu)
                        const selectedRows = dt.rows({ selected: true });
                        if (selectedRows.count() > 0) {
                            let selectedLogin = [];
                            // On récupère le login de chaque ligne sélectionnée
                            selectedRows.every(function () {
                                selectedLogin.push(this.data()[0]);
                            });
                            $('#keepListLogin').val(selectedLogin.join(',')); // On met les logins dans le champ caché du form
                            $('#keepModal').modal('show'); // On affiche la modal pour obtenir la raison et confirmer
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    }
                },
                {
                    text: 'Bloquer',
                    action: function (e, dt, node, config, cb) {
                        const selectedRows = dt.rows({ selected: true });
                        if (selectedRows.count() > 0) {
                            let selectedLogin = [];
                            selectedRows.every(function () {
                                selectedLogin.push(this.data()[0]);
                            });
                            $('#blockListLogin').val(selectedLogin.join(','));
                            $('#blockModal').modal('show');
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    },
                },
                {
                    text: 'Débloquer',
                    action: function (e, dt, node, config, cb) {
                        const selectedRows = dt.rows({ selected: true });
                        if (selectedRows.count() > 0) {
                            let loginList = [];
                            selectedRows.every(function () {
                                loginList.push(this.data()[0]);
                            });
                            $('#unblockListLogin').val(loginList.join(','));
                            $('#unblockModal').modal('show');
                        } else {
                            alert('Sélectionnez au moins une ligne');
                        }
                    },
                }
            ]
        },
    },
});