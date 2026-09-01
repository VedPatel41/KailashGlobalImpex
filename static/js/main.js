/**
 * KAILASH GLOBAL IMPEX — ENTERPRISE B2B EXPORT FRONTEND SCRIPT
 * GSAP Animations, Interactive Trade Corridors Canvas,
 * Sticky Header, Mobile Drawer, and AJAX Inquiry Submissions.
 */

document.addEventListener('DOMContentLoaded', () => {
  initStickyHeader();
  initMobileDrawer();
  initHeroSlideshow();
  initTradeCorridorsCanvas();
  initInquiryFormAjax();
});

/* ==========================================================================
   HERO PORT BACKGROUND SLIDESHOW (Subtle 7s Crossfade & Ken Burns)
   ========================================================================== */
function initHeroSlideshow() {
  const container = document.querySelector('.hero-slideshow-container');
  const slides = document.querySelectorAll('.hero-slideshow-container .hero-slide');
  if (!container || !slides || slides.length < 2) return;

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) return;

  let currentIdx = 0;
  let intervalId = null;
  const slideInterval = 7000;

  const start = () => {
    if (intervalId) return;
    intervalId = setInterval(() => {
      slides[currentIdx].classList.remove('active');
      currentIdx = (currentIdx + 1) % slides.length;
      slides[currentIdx].classList.add('active');
    }, slideInterval);
  };

  const stop = () => {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  };

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) start();
        else stop();
      });
    }, { threshold: 0.05 });
    observer.observe(container);
  } else {
    start();
  }
}

/* ==========================================================================
   1. STICKY HEADER & SCROLL BEHAVIOR
   ========================================================================== */

/* ==========================================================================
   2. STICKY HEADER & SCROLL BEHAVIOR
   ========================================================================== */
function initStickyHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const onScroll = () => {
    if (window.scrollY > 30) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ==========================================================================
   3. MOBILE NAVIGATION DRAWER
   ========================================================================== */
function initMobileDrawer() {
  const toggleBtn = document.querySelector('.mobile-toggle');
  const drawer = document.querySelector('.mobile-drawer');
  const closeBtn = document.querySelector('.drawer-close');
  const backdrop = document.querySelector('.drawer-backdrop');
  const links = document.querySelectorAll('.drawer-nav .nav-link');

  if (!toggleBtn || !drawer) return;

  const openDrawer = () => {
    drawer.classList.add('open');
    if (backdrop) backdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  const closeDrawer = () => {
    drawer.classList.remove('open');
    if (backdrop) backdrop.classList.remove('active');
    document.body.style.overflow = '';
  };

  toggleBtn.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (backdrop) backdrop.addEventListener('click', closeDrawer);
  links.forEach(link => link.addEventListener('click', closeDrawer));
}

/* ==========================================================================
   4. GLOBAL TRADE CORRIDORS ANIMATED CANVAS (India -> International Hubs)
   ========================================================================== */
function initTradeCorridorsCanvas() {
  const canvas = document.getElementById('trade-corridor-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let animationId;
  let width, height;

  const resize = () => {
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = rect.height;
  };

  resize();
  window.addEventListener('resize', resize);

  const originNode = { name: 'Gujarat, India', x: 0.52, y: 0.52, isOrigin: true };
  const destinationNodes = [
    { name: 'Middle East (Jebel Ali / Jeddah)', x: 0.42, y: 0.48 },
    { name: 'Western Europe (Rotterdam / Hamburg)', x: 0.32, y: 0.32 },
    { name: 'North America (East Coast Hubs)', x: 0.16, y: 0.35 },
    { name: 'Southeast Asia (Singapore / Port Klang)', x: 0.68, y: 0.62 },
    { name: 'East Asia (Busan / Yokohama)', x: 0.82, y: 0.40 },
    { name: 'East Africa (Mombasa / Durban)', x: 0.46, y: 0.70 },
  ];

  const particles = [];
  destinationNodes.forEach((dest, idx) => {
    for (let i = 0; i < 3; i++) {
      particles.push({
        destIndex: idx,
        progress: (i / 3) + Math.random() * 0.2,
        speed: 0.003 + Math.random() * 0.002,
        size: 2.5 + Math.random() * 1.5,
      });
    }
  });

  let pulseAngle = 0;

  function render() {
    ctx.clearRect(0, 0, width, height);

    pulseAngle += 0.04;
    const originPx = { x: originNode.x * width, y: originNode.y * height };

    // Background Subtle Grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    const step = 40;
    for (let x = 0; x < width; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Connecting Arcs to Destinations
    destinationNodes.forEach((dest) => {
      const destPx = { x: dest.x * width, y: dest.y * height };
      const midX = (originPx.x + destPx.x) / 2;
      const midY = (originPx.y + destPx.y) / 2 - 40;

      ctx.beginPath();
      ctx.moveTo(originPx.x, originPx.y);
      ctx.quadraticCurveTo(midX, midY, destPx.x, destPx.y);
      ctx.strokeStyle = 'rgba(197, 168, 103, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.beginPath();
      ctx.arc(destPx.x, destPx.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#c5a867';
      ctx.fill();

      ctx.font = '11px "Plus Jakarta Sans", sans-serif';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.fillText(dest.name, destPx.x + 8, destPx.y + 4);
    });

    // Traveling Particles along Bezier Arcs
    particles.forEach(p => {
      p.progress += p.speed;
      if (p.progress > 1) p.progress = 0;

      const dest = destinationNodes[p.destIndex];
      const destPx = { x: dest.x * width, y: dest.y * height };
      const midX = (originPx.x + destPx.x) / 2;
      const midY = (originPx.y + destPx.y) / 2 - 40;

      const t = p.progress;
      const currX = Math.pow(1 - t, 2) * originPx.x + 2 * (1 - t) * t * midX + Math.pow(t, 2) * destPx.x;
      const currY = Math.pow(1 - t, 2) * originPx.y + 2 * (1 - t) * t * midY + Math.pow(t, 2) * destPx.y;

      ctx.beginPath();
      ctx.arc(currX, currY, p.size, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#c5a867';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // Origin Gujarat Node
    const pulseSize = 8 + Math.sin(pulseAngle) * 4;
    ctx.beginPath();
    ctx.arc(originPx.x, originPx.y, 16 + pulseSize, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(197, 168, 103, 0.15)';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(originPx.x, originPx.y, 8, 0, Math.PI * 2);
    ctx.fillStyle = '#dfc285';
    ctx.shadowColor = '#c5a867';
    ctx.shadowBlur = 15;
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.font = 'bold 12px "Outfit", sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.fillText('ORIGIN: Gujarat, India', originPx.x - 60, originPx.y - 20);

    if (isCanvasVisible) {
      animationId = requestAnimationFrame(render);
    } else {
      animationId = null;
    }
  }

  let isCanvasVisible = false;
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        isCanvasVisible = entry.isIntersecting;
        if (isCanvasVisible && !animationId) {
          render();
        }
      });
    }, { threshold: 0.05 });
    observer.observe(canvas);
  } else {
    isCanvasVisible = true;
    render();
  }
}

/* ==========================================================================
   5. INQUIRY FORM SUBMISSION (AJAX with Toasts)
   ========================================================================== */
function initInquiryFormAjax() {
  const forms = document.querySelectorAll('.js-inquiry-form');

  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : 'Submit';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span>Processing Inquiry...</span>`;
      }

      const formData = new FormData(form);
      formData.append('is_ajax', '1');

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          }
        });

        const data = await response.json();

        if (response.ok && data.success) {
          showToast(data.message, 'success');
          form.reset();
        } else {
          showToast(data.message || 'Submission error. Please check your inputs.', 'error');
        }
      } catch (err) {
        showToast('Network error while transmitting your inquiry. Please try again or reach out directly.', 'error');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }
      }
    });
  });
}

/* ==========================================================================
   6. TOAST NOTIFICATION UTILITY
   ========================================================================== */
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'error' ? 'toast-error' : ''}`;
  toast.innerHTML = `
    <div style="display:flex;align-items:center;gap:0.75rem;">
      <span style="font-weight:700;font-size:1.1rem;">${type === 'error' ? '⚠' : '✓'}</span>
      <span>${message}</span>
    </div>
    <button style="background:none;border:none;color:#ffffff;font-size:1.2rem;cursor:pointer;margin-left:1rem;" aria-label="Close">&times;</button>
  `;

  const closeBtn = toast.querySelector('button');
  closeBtn.addEventListener('click', () => toast.remove());

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 6000);
}
