/**
 * KAILASH GLOBAL IMPEX — CRM ADMIN DASHBOARD SCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
  initStatusChangers();
  initAutoSubmitFilters();
});

function initStatusChangers() {
  const quickStatusSelects = document.querySelectorAll('.js-quick-status');

  quickStatusSelects.forEach(select => {
    select.addEventListener('change', async (e) => {
      const url = select.dataset.url;
      const newStatus = select.value;
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

      try {
        const formData = new FormData();
        formData.append('status', newStatus);
        if (csrfToken) formData.append('csrfmiddlewaretoken', csrfToken);

        const res = await fetch(url, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          }
        });

        const data = await res.json();
        if (res.ok && data.success) {
          // Update status badge if on page
          const row = select.closest('tr');
          if (row) {
            const badge = row.querySelector('.badge');
            if (badge) {
              badge.className = `badge badge-${data.new_status}`;
              badge.textContent = data.status_display;
            }
          }
        } else {
          alert('Failed to update status: ' + (data.message || 'Unknown error'));
        }
      } catch (err) {
        alert('Communication error updating status.');
      }
    });
  });
}

function initAutoSubmitFilters() {
  const filterForm = document.querySelector('.crm-filter-form');
  if (!filterForm) return;

  const autoSelects = filterForm.querySelectorAll('select');
  autoSelects.forEach(select => {
    select.addEventListener('change', () => {
      filterForm.submit();
    });
  });
}
