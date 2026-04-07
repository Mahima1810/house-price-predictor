const form = document.getElementById('predictForm');
const areaEl = document.getElementById('area');
const roomsEl = document.getElementById('rooms');
const locationEl = document.getElementById('location');
const btn = document.getElementById('predictBtn');
const messageEl = document.getElementById('message');
const resultEl = document.getElementById('result');

function setLoading(isLoading) {
  if (isLoading) {
    btn.classList.add('loading');
    btn.setAttribute('disabled', 'true');
    messageEl.classList.remove('error');
    messageEl.textContent = 'Predicting...';
  } else {
    btn.classList.remove('loading');
    btn.removeAttribute('disabled');
  }
}

function showError(msg) {
  messageEl.classList.add('error');
  messageEl.textContent = msg;
}

function clearStatus() {
  messageEl.classList.remove('error');
  messageEl.textContent = '';
}

function formatMoney(n) {
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(n);
  } catch {
    return `$${Math.round(n).toLocaleString()}`;
  }
}

function validateInputs(area, rooms, location) {
  if (!Number.isFinite(area) || area <= 0) return 'Area must be greater than 0.';
  if (!Number.isFinite(rooms) || !Number.isInteger(rooms) || rooms < 1)
    return 'Rooms must be a whole number (min 1).';
  if (!Number.isFinite(location) || location < 1 || location > 10)
    return 'Location score must be between 1 and 10.';
  return null;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  resultEl.textContent = '';
  clearStatus();

  const area = Number(areaEl.value);
  const rooms = Number(roomsEl.value);
  const location = Number(locationEl.value);

  const validationError = validateInputs(area, rooms, location);
  if (validationError) {
    showError(validationError);
    return;
  }

  setLoading(true);

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        area,
        rooms,
        location,
      }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = data && data.error ? data.error : 'Request failed.';
      showError(msg);
      return;
    }

    const price = data && typeof data.predicted_price === 'number' ? data.predicted_price : NaN;
    if (!Number.isFinite(price)) {
      showError('Invalid prediction response from server.');
      return;
    }

    messageEl.classList.remove('error');
    messageEl.textContent = 'Done.';
    resultEl.textContent = `Predicted house price: ${formatMoney(price)}`;
  } catch (err) {
    showError('Could not connect to the server. Is the backend running?');
  } finally {
    setLoading(false);
  }
});
