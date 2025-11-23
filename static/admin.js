// Admin Panel JavaScript
let blogToDelete = null;

function deleteBlog(blogId) {
  blogToDelete = blogId;
  document.getElementById('deleteModal').classList.remove('hidden');
  document.getElementById('deleteModal').classList.add('flex');
}

function hideDeleteModal() {
  document.getElementById('deleteModal').classList.add('hidden');
  document.getElementById('deleteModal').classList.remove('flex');
  blogToDelete = null;
}

document.addEventListener('DOMContentLoaded', function() {
  // Delete button event listeners
  const deleteButtons = document.querySelectorAll('.delete-blog-btn');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
      const blogId = this.getAttribute('data-blog-id');
      deleteBlog(blogId);
    });
  });

  const confirmDeleteBtn = document.getElementById('confirmDelete');
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
      if (blogToDelete) {
        // Form oluştur ve gönder
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/blog/delete/${blogToDelete}`;
        document.body.appendChild(form);
        form.submit();
      }
    });
  }

  // Modal dışına tıklanınca kapat
  const deleteModal = document.getElementById('deleteModal');
  if (deleteModal) {
    deleteModal.addEventListener('click', function(e) {
      if (e.target === this) {
        hideDeleteModal();
      }
    });
  }
});
