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
    dom: "Qfrtip", //Affiche seulement la recherche avancée avec la congifuration par défaut
});

function use_template(title ,newSubject, newMessage){
    let subject = document.getElementById('subject');
    let message = document.getElementById('message');
    subject.value = newSubject;
    message.value = newMessage;
    $('#Use'+title).modal('hide');
}