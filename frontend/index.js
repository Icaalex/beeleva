  const API = 'http://127.0.0.1:8000';

  // Show toast notification
  function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.className = 'toast', 3000);
  }

  // Format date nicely
  function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', {
      day: 'numeric', month: 'short',
      hour: '2-digit', minute: '2-digit'
    });
  }

  // Submit inquiry to Beeleva
  async function submitInquiry() {
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();

    // Basic validation
    if (!name || !email || !message) {
      showToast('Please fill in all fields', 'error');
      return;
    }

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Beeleva is thinking...';

    try {
      // Send to FastAPI backend
      const res = await axios.post(`${API}/inquiry`, { name, email, message });
      const data = res.data;

      // Show response
      const box = document.getElementById('responseBox');
      const badge = document.getElementById('returningBadge');
      const text = document.getElementById('responseText');

      // Show memory badge if returning customer
      badge.style.display = data.is_returning_customer ? 'inline-block' : 'none';
      text.textContent = data.message;
      box.className = 'response-box visible';

      showToast('✅ Response sent to customer email');

      // Clear form
      document.getElementById('name').value = '';
      document.getElementById('email').value = '';
      document.getElementById('message').value = '';

      // Reload inquiry feed
      loadInquiries();

    } catch (err) {
      showToast('Something went wrong. Is the backend running?', 'error');
      console.error(err);
    }

    btn.disabled = false;
    btn.innerHTML = 'Send to Beeleva';
  }

  // Load all inquiries from backend
  async function loadInquiries() {
    try {
      const res = await axios.get(`${API}/inquiries`);
      const inquiries = res.data;

      // Update stats
      document.getElementById('totalInquiries').textContent = inquiries.length;

      const list = document.getElementById('inquiryList');

      if (inquiries.length === 0) {
        list.innerHTML = `
          <div class="empty-state">
            <div class="big">📭</div>
            No inquiries yet. Submit one to get started.
          </div>`;
        return;
      }

      // Render each inquiry
      list.innerHTML = inquiries.map((inq, i) => `
        <div class="inquiry-item" id="inq-${i}">
          <div class="inquiry-header">
            <span class="inquiry-email">${inq.customer_email}</span>
            <span class="inquiry-time">${formatDate(inq.created_at)}</span>
          </div>
          <div class="inquiry-message">"${inq.message}"</div>
          <button class="toggle-btn" onclick="toggleResponse(${i})">
            View Beeleva's response ▾
          </button>
          <div class="inquiry-response">${inq.response}</div>
        </div>
      `).join('');

    } catch (err) {
      console.error('Could not load inquiries:', err);
    }
  }

  // Toggle response visibility
  function toggleResponse(i) {
    const item = document.getElementById(`inq-${i}`);
    const isExpanded = item.classList.contains('expanded');
    item.classList.toggle('expanded');
    item.querySelector('.toggle-btn').textContent =
      isExpanded ? 'View Beeleva\'s response ▾' : 'Hide response ▴';
  }

  // Load customer count
  async function loadStats() {
    try {
      const res = await axios.get(`${API}/inquiries`);
      const emails = [...new Set(res.data.map(i => i.customer_email))];
      document.getElementById('totalCustomers').textContent = emails.length;
    } catch(e) {}
  }

  // Initialize dashboard
  window.onload = () => {
    loadInquiries();
    loadStats();
    // Auto-refresh every 30 seconds
    setInterval(() => {
      loadInquiries();
      loadStats();
    }, 30000);
  };
