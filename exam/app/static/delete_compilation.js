const deleteCompilationModalEl = document.getElementById('deleteCompilationModal');
deleteCompilationModalEl.addEventListener('show.bs.modal', function (event) {
    let url = event.relatedTarget.dataset.url;
    let form = this.querySelector('form');
    form.action = url;
    let span = this.querySelector('.delete-compilation-name');
    span.textContent = event.relatedTarget.dataset.name;
});