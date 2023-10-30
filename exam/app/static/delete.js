const deleteModalEl = document.getElementById('deleteModal');
deleteModalEl.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url;
    let span = this.querySelector('.delete-book-name');
    span.textContent = event.relatedTarget.dataset.name;
});

const toCompilationModalEl = document.getElementById('addBookInCompilationModal');
toCompilationModalEl.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url;
    let span = this.querySelector('.add-book-in-compilation-book-name');
    span.textContent = event.relatedTarget.dataset.name;
});