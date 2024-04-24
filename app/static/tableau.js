let table = new DataTable('#myTable', {
    select: true,
    responsive: true,
    dom:
        "<'row'<'col-sm-12'Q>>" + // SearchBuilder
        "<'row'<'col-sm-12'tr>>" + // Tableau pleine largeur
        "<'row'<'col-sm-12'B>>"+  //Boutons
        "<'row'<'col-sm-9'i><'col-sm-3'p>>", // Info et pagination en bas à gauche, personnalisation à droite
    buttons: [
        {
            text: 'Supprimer',
            action: function (e, dt, node, config, cb) {
                const selectedRows = dt.rows({ selected: true });
                if (selectedRows.count() > 0) {
                    //Affiche chaque ligne sélectionné dans la console
                    selectedRows.every(function () {
                        console.log("Supprime " +this.data()[0]);
                    });
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