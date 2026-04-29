import { generateData, uploadFiles, reconcileData } from './api.js';
import { showAlert, showLoader, hideSections, updateDashboard } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const btnGenerate = document.getElementById('btn-generate');
    const btnReconcile = document.getElementById('btn-reconcile');
    const uploadForm = document.getElementById('upload-form');
    
    let currentReportId = null;

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const txFile = document.getElementById('file-tx').files[0];
            const setFile = document.getElementById('file-set').files[0];
            
            if (!txFile || !setFile) {
                showAlert('Please select both files to upload.', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('transactions', txFile);
            formData.append('settlements', setFile);

            showAlert('Uploading files...', 'info');
            try {
                const data = await uploadFiles(formData);
                showAlert('Files uploaded successfully! You can now run reconciliation.', 'success');
                // Point to the newly uploaded files
                window.currentTxFile = 'uploaded_transactions.csv';
                window.currentSetFile = 'uploaded_settlements.csv';
            } catch (error) {
                showAlert(`Failed to upload files: ${error.message}`, 'error');
            }
        });
    }

    btnGenerate.addEventListener('click', async () => {
        showAlert('Generating synthetic data...', 'info');
        try {
            await generateData();
            showAlert('Data generated successfully! You can now run reconciliation.', 'success');
            window.currentTxFile = 'transactions.csv';
            window.currentSetFile = 'settlements.csv';
        } catch (error) {
            showAlert(`Failed to generate data: ${error.message}`, 'error');
        }
    });

    btnReconcile.addEventListener('click', async () => {
        showLoader(true);
        hideSections();
        showAlert('Running reconciliation engine and generating AI explanations...', 'info');
        
        const txFile = window.currentTxFile || 'transactions.csv';
        const setFile = window.currentSetFile || 'settlements.csv';

        try {
            const data = await reconcileData(txFile, setFile);
            showAlert('Reconciliation complete.', 'success');
            currentReportId = data.report_id;
            updateDashboard(data);
        } catch (error) {
            showAlert(`Failed to reconcile data: ${error.message}`, 'error');
        } finally {
            showLoader(false);
        }
    });

    document.getElementById('btn-download').addEventListener('click', () => {
        if (currentReportId) {
            window.open(`/report/${currentReportId}`, '_blank');
        }
    });
});
