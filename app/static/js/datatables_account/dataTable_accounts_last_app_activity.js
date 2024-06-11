$(document).ready(function() {
    let table = new DataTable('#accountTable', {
        serverSide: true,
        processing: true,
        ajax: {
            url: "./api",
            type: 'GET',
        },
        columns: [
            { data: 'Login' },
            { data: "Groupe" },
            {
                data: "Date de dernière connexion",
                type: 'date',
                render: function(data, type, row) {
                    return moment(data).format('YYYY-MM-DD HH:mm:ss');
                }
            },
            { data: "Type" },
            { data: "Adresse IP" },
            { data: "Service" },
            {
                data: null,
                render: function(data, type, row) {
                    return '<a href="../account/%login/details" class="btn btn-outline-primary btn-sm disable">'
                        .replace('%login', row['Login']) +
                        '<img src="../../static/svg/search.svg" alt="Icone loupe"> </a>';
                },
                orderable: false,
                searchable: false
            }
        ],
        select: true,
        responsive: true,
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
                buttons: [
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
                buttons: [
                    {
                        text: 'Supprimer',
                        action: function (e, dt, node, config, cb) {
                            const selectedRows = dt.rows({ selected: true });
                            if (selectedRows.count() > 0) {
                                let selectedLogin = [];
                                selectedRows.every(function () {
                                    selectedLogin.push(this.data().Login);
                                });
                                $('#deleteListLogin').val(selectedLogin.join(','));
                                $('#deleteModal').modal('show');
                            } else {
                                alert('Sélectionnez au moins une ligne');
                            }
                        },
                        className: 'btn-danger'
                    },
                    // Ajoutez d'autres actions ici...
                ]
            },
        },
        initComplete: function () {
            this.api().columns().every(function () {
                if (this.footer().textContent === '' || this.footer().textContent === 'Plus de détails') {
                    return;
                }
                let column = this;
                let title = column.footer().textContent;
                let input = document.createElement('input');
                input.placeholder = title;
                column.footer().replaceChildren(input);
                input.addEventListener('keyup', function () {
                    if (column.search() !== this.value) {
                        column.search(this.value).draw();
                    }
                });
            });
        }
    });
});
