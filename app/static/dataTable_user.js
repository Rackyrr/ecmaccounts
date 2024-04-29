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
    //Organisation visuelle du tableau
    dom:
        "<'row'<'col-sm-12'Q>>" + // SearchBuilder
        "<'row'<'col-sm-12'tr>>" + // Tableau pleine largeur
        "<'row'<'col-sm-12'B>>"+  //Boutons
        "<'row'<'col-sm-9'i><'col-sm-3'p>>", // Info et pagination en bas à gauche, personnalisation à droite
    buttons: [
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
        },
        {
            text:'Envoyer un mail',
            action
            : function (e, dt, node, config, cb) {
                const selectedRows = dt.rows({ selected: true });
                if (selectedRows.count() > 0) {
                    //Affiche chaque ligne sélectionné dans la console
                    selectedRows.every(function () {
                        console.log("Envoyer mail " + this.data()[0]);
                    });
                } else {
                    alert('Sélectionnez au moins une ligne');
                }
            },
        }
    ]
});