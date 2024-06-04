$(document).ready(function() {
    let password_expiration = $('#password_expiration').val();

    let table = new DataTable('#accountTable', {
        //Configuration Server Side
        serverSide: true,
        processing: true,
        ajax: {
            url: "./api",
            type: 'GET',
            data: function (d) {
                d.password_expiration = password_expiration;
            }
        },
        columns: [
            { data: 'Login'},
            { data: "Email" },
            { data: "Groupe"},
            {
                data: "Dernier changement de mot de passe",
                type: 'date',
                render: function(data, type, row) {
                    return moment(data).format('YYYY-MM-DD HH:mm:ss');
                }
            },
            { data: "Jamais modifié", type: 'boolean' },
            { data: "locked" , type: 'boolean'},
            {
                data: null, render: function (data, type, row) {
                    return '<a href="../account/%login/details" class="btn btn-outline-primary btn-sm disable">'.replace('%login', row['Login']) +
                        '<img src="../static/svg/search.svg" alt="Icone loupe"> </a>'
                },
                orderable: false,
                searchable: false
            }
        ],

        //Selection des lignes possibles
        select: true,
        responsive: true,
        //Langue du tableau
        language: {
            url: 'https:////cdn.datatables.net/plug-ins/2.0.5/i18n/fr-FR.json',
            paginate: {
                first: '«',
                previous: '‹',
                next: '›',
                last: '»'
            },
            select: {
                columns: "",
                cells: "",
            }
        },
        layout: {
            top2End: {
                buttons: [ //Boutons selectionner tout et deselectionner tout
                    {
                        text: "Selectionner tout",
                        extend: 'selectAll',
                        selectorModifier: {
                            search: 'applied',
                        }
                    },
                    {
                        text: "Deselectionner tout",
                        extend: 'selectNone',
                        selectorModifier: {
                            search: 'applied',
                        }
                    }
                ]
            },
            bottom: {
                buttons: [ //Boutons d'actions
                    {
                        text: 'Supprimer',
                        action: function (e, dt, node, config, cb) {
                            // On récupère les lignes sélectionnées dans le tableau (en bleu)
                            const selectedRows = dt.rows({selected: true});
                            // Pour supprimer, il faut au moins une ligne sélectionnée
                            if (selectedRows.count() > 0) {
                                let selectedLogin = [];
                                // On récupère le login de chaque ligne sélectionnée
                                selectedRows.every(function () {
                                    selectedLogin.push(this.data().Login);
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
                            const selectedRows = dt.rows({selected: true});
                            if (selectedRows.count() > 0) {
                                let loginList = [];
                                selectedRows.every(function () {
                                    loginList.push(this.data().Login);
                                });
                                $('#cancelDeleteListLogin').val(loginList.join(','));
                                $('#cancelDeleteModal').modal('show');
                            } else {
                                alert('Sélectionnez au moins une ligne');
                            }
                        }
                    },
                    {
                        text: 'Envoyer un mail',
                        action: function (e, dt, node, config, cb) {
                            const selectedRows = dt.rows({selected: true});
                            if (selectedRows.count() > 0) {
                                let mailList = [];
                                //Affiche chaque ligne sélectionné dans la console
                                selectedRows.every(function () {
                                    mailList.push(this.data().Email);
                                });
                                $('#listMail').val(mailList.join(','));
                                $('#sendMailList').submit()
                            } else {
                                alert('Sélectionnez au moins une ligne');
                            }
                        }
                    },
                    {
                        text: 'Garder le(s) compte(s)',
                        action: function (e, dt, node, config, cb) {
                            // On récupère les lignes sélectionnées dans le tableau (en bleu)
                            const selectedRows = dt.rows({selected: true});
                            if (selectedRows.count() > 0) {
                                let selectedLogin = [];
                                // On récupère le login de chaque ligne sélectionnée
                                selectedRows.every(function () {
                                    selectedLogin.push(this.data().Login);
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
                            const selectedRows = dt.rows({selected: true});
                            if (selectedRows.count() > 0) {
                                let selectedLogin = [];
                                selectedRows.every(function () {
                                    selectedLogin.push(this.data().Login);
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
                            const selectedRows = dt.rows({selected: true});
                            if (selectedRows.count() > 0) {
                                let loginList = [];
                                selectedRows.every(function () {
                                    loginList.push(this.data().Login);
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
        initComplete: function () {
            this.api().columns().every(function () {
                //Ne pas executer la recherche pour la colonne des boutons
                if (this.footer().textContent==='' || this.footer().textContent==='Plus de détails') {
                    return;
                }
                let column = this;
                let title = column.footer().textContent;

                // On créer l'input pour la recherche
                let input = document.createElement('input');
                input.placeholder = title;
                column.footer().replaceChildren(input);

                // On ajoute un event listener sur l'input pour effectuer la recherche
                input.addEventListener('keyup', function () {
                    if (column.search() !== this.value) {
                        // Draw envoie la requête au serveur pour effectuer la recherche
                        column.search(this.value).draw();
                    }
                });
            });
        }
    });

    $('#password_expiration').on('change', function () {
        password_expiration = $(this).val();
        table.ajax.reload();
    });
});