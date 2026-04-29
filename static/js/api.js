export async function generateData() {
    const response = await fetch('/generate-data', { method: 'POST' });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${response.status}`);
    }
    return await response.json();
}

export async function uploadFiles(formData) {
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${response.status}`);
    }
    return await response.json();
}

export async function reconcileData(txFile, setFile) {
    const response = await fetch(`/reconcile?tx_file=${encodeURIComponent(txFile)}&set_file=${encodeURIComponent(setFile)}`);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${response.status}`);
    }
    return await response.json();
}
