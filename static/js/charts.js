let barChartInstance = null;
let pieChartInstance = null;
let mismatchChartInstance = null;

export function drawBarChart(summary) {
    const ctx = document.getElementById('barChart').getContext('2d');
    if (barChartInstance) barChartInstance.destroy();

    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Platform Transactions', 'Bank Settlements'],
            datasets: [{
                label: 'Count',
                data: [summary.total_transactions, summary.total_settlements],
                backgroundColor: ['#3b82f6', '#1e3a8a'],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

export function drawPieChart(issueCounts) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    if (pieChartInstance) pieChartInstance.destroy();

    const labels = Object.keys(issueCounts);
    const data = Object.values(issueCounts);
    const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#64748b'];

    pieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            },
            cutout: '60%'
        }
    });
}

export function drawMismatchChart(mismatchAmounts) {
    const ctx = document.getElementById('mismatchChart').getContext('2d');
    if (mismatchChartInstance) mismatchChartInstance.destroy();

    const labels = Object.keys(mismatchAmounts);
    const data = Object.values(mismatchAmounts).map(val => parseFloat(val.toFixed(2)));
    const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#64748b'];

    mismatchChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Transaction Volume ($)',
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
