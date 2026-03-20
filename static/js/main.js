// Auto-dismiss alerts after 6 seconds
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.alert-dismissible').forEach(function (el) {
            try { new bootstrap.Alert(el).close(); } catch(e) {}
        });
    }, 6000);
});
