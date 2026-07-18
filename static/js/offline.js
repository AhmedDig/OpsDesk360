let offlineQueue = JSON.parse(localStorage.getItem('offlineSales') || '[]');
let lastSync = localStorage.getItem('lastSync') || Date.now();
const OFFLINE_LIMIT_HOURS = 4;

function updateOfflineIndicator() {
    const indicator = document.getElementById('offline-status');
    if (!indicator) return;
    if (!navigator.onLine) {
        const hoursOffline = (Date.now() - lastSync) / (1000 * 60 * 60);
        const pendingCount = offlineQueue.length;
        indicator.innerHTML = `⚠️ Offline – ${pendingCount} sale(s) pending. Last sync: ${new Date(Number(lastSync)).toLocaleTimeString()}`;
        indicator.classList.add('text-orange-600');
        if (hoursOffline >= OFFLINE_LIMIT_HOURS) {
            indicator.innerHTML = '🔒 Offline limit exceeded. Please reconnect to process sales.';
            indicator.classList.add('text-red-600');
            const btn = document.getElementById('checkout-btn');
            if (btn) btn.disabled = true;
        } else {
            const btn = document.getElementById('checkout-btn');
            if (btn) btn.disabled = false;
        }
    } else {
        indicator.innerHTML = `✅ Online – ${offlineQueue.length} sale(s) pending sync.`;
        indicator.classList.remove('text-orange-600', 'text-red-600');
        syncOfflineSales();
    }
}

async function syncOfflineSales() {
    if (offlineQueue.length === 0) return;
    if (!navigator.onLine) return;
    try {
        const response = await fetch('/pos/sync-offline/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ sales: offlineQueue })
        });
        const result = await response.json();
        if (result.results) {
            offlineQueue = offlineQueue.filter((_, idx) => result.results[idx]?.status === 'failed');
            localStorage.setItem('offlineSales', JSON.stringify(offlineQueue));
            localStorage.setItem('lastSync', Date.now());
            lastSync = Date.now();
            updateOfflineIndicator();
            if (offlineQueue.length === 0 && window.location.pathname === '/pos/') {
                location.reload();
            }
        }
    } catch (err) {
        console.error('Sync failed', err);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function triggerToast(message, type = 'info') {
    if (typeof window !== 'undefined' && window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}

function interceptCheckout(e) {
    if (!navigator.onLine) {
        e.preventDefault();
        const hoursOffline = (Date.now() - lastSync) / (1000 * 60 * 60);
        if (hoursOffline >= OFFLINE_LIMIT_HOURS) {
            triggerToast('Offline limit exceeded. Please connect to internet to process sale.', 'error');
            return;
        }
        const cartItems = document.querySelectorAll('#cart-items li');
        if (cartItems.length === 0) {
            triggerToast('Cart is empty.', 'warning');
            return;
        }
        const saleData = {
            customer_id: document.querySelector('select[name="customer"]')?.value || null,
            payment_method: document.querySelector('input[name="payment_method"]')?.value || 'cash',
            discount: parseFloat(document.querySelector('input[name="discount"]')?.value) || 0,
            tax: parseFloat(document.querySelector('input[name="tax"]')?.value) || 0,
            items: []
        };
        cartItems.forEach(li => {
            const itemId = li.getAttribute('data-item-id');
            const unitPrice = li.getAttribute('data-unit-price');
            const qtyInput = li.querySelector('input[type="number"]');
            if (itemId && unitPrice && qtyInput) {
                saleData.items.push({
                    item_id: parseInt(itemId),
                    quantity: parseInt(qtyInput.value),
                    unit_price: parseFloat(unitPrice)
                });
            }
        });
        offlineQueue.push(saleData);
        localStorage.setItem('offlineSales', JSON.stringify(offlineQueue));
        updateOfflineIndicator();
        triggerToast('Sale saved offline. It will sync when you reconnect.', 'success');
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }
}

// Event delegation – listen for submit on any form with id="checkout-form"
document.body.addEventListener('submit', function(e) {
    if (e.target && e.target.id === 'checkout-form') {
        interceptCheckout(e);
    }
});

updateOfflineIndicator();
setInterval(() => {
    if (navigator.onLine) syncOfflineSales();
    else updateOfflineIndicator();
}, 30000);

window.addEventListener('online', () => {
    updateOfflineIndicator();
    syncOfflineSales();
});
window.addEventListener('offline', updateOfflineIndicator);