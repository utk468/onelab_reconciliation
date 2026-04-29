import { drawBarChart, drawPieChart, drawMismatchChart } from './charts.js';

export function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    alertContainer.textContent = message;
    alertContainer.className = 'mb-6 p-4 rounded-md shadow-sm block';
    
    if (type === 'error') {
        alertContainer.classList.add('bg-red-50', 'text-red-800', 'border', 'border-red-200');
    } else if (type === 'success') {
        alertContainer.classList.add('bg-green-50', 'text-green-800', 'border', 'border-green-200');
    } else {
        alertContainer.classList.add('bg-blue-50', 'text-blue-800', 'border', 'border-blue-200');
    }
}

export function showLoader(show) {
    const loader = document.getElementById('loader');
    loader.style.display = show ? 'flex' : 'none';
}

export function hideSections() {
    document.getElementById('charts-section').classList.add('hidden');
    document.getElementById('table-section').classList.add('hidden');
}

export function updateDashboard(data) {
    // Update summary cards
    document.getElementById('val-transactions').textContent = data.summary.total_transactions;
    document.getElementById('val-settlements').textContent = data.summary.total_settlements;
    document.getElementById('val-mismatch').textContent = `$${data.summary.total_mismatch_amount.toFixed(2)}`;
    document.getElementById('val-issues').textContent = data.summary.issues_count;

    // Populate Table
    const tbody = document.getElementById('issues-tbody');
    tbody.innerHTML = '';

    const issueCounts = {};
    const mismatchAmounts = {};

    data.issues.forEach(issue => {
        // Count for pie chart
        issueCounts[issue.issue_type] = (issueCounts[issue.issue_type] || 0) + 1;

        // Amount mismatch for new chart
        const pAmt = Math.abs(issue.platform_amount || 0);
        const bAmt = Math.abs(issue.bank_amount || 0);
        const val = Math.max(pAmt, bAmt);
        mismatchAmounts[issue.issue_type] = (mismatchAmounts[issue.issue_type] || 0) + val;

        const tr = document.createElement('tr');
        
        // Highlight logic
        if (issue.issue_type === 'Amount Mismatch' || issue.issue_type === 'Missing Settlement' || issue.issue_type === 'Extra Settlement') {
            tr.className = 'issue-row-red';
        } else if (issue.issue_type === 'Duplicate Transaction' || issue.issue_type === 'Delayed Settlement' || issue.issue_type === 'Refund Inconsistency') {
            tr.className = 'issue-row-yellow';
        } else {
            tr.className = 'issue-row-gray';
        }

        const formatCurrency = (val) => val !== null ? `$${val.toFixed(2)}` : '-';

        tr.innerHTML = `
            <td class="px-6 py-4 font-medium text-gray-900">${issue.txn_id}</td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 bg-white bg-opacity-50 rounded-full text-xs font-semibold shadow-sm border border-gray-200">
                    ${issue.issue_type}
                </span>
            </td>
            <td class="px-6 py-4 text-gray-600">${formatCurrency(issue.platform_amount)}</td>
            <td class="px-6 py-4 text-gray-600">${formatCurrency(issue.bank_amount)}</td>
            <td class="px-6 py-4 text-gray-600 text-sm italic">"${issue.explanation}"</td>
        `;
        tbody.appendChild(tr);
    });

    // Show sections
    document.getElementById('charts-section').classList.remove('hidden');
    document.getElementById('table-section').classList.remove('hidden');

    // Draw Charts
    drawBarChart(data.summary);
    drawPieChart(issueCounts);
    drawMismatchChart(mismatchAmounts);
}
