$(document).ready(function() {
    let table = new DataTable('#userTable', {
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
    });
});
