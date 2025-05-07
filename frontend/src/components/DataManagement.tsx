import React, { useRef } from 'react';
import axios from 'axios';

interface DataManagementProps {
    onImportSuccess: () => void;
}

const DataManagement: React.FC<DataManagementProps> = ({ onImportSuccess }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleExport = async () => {
        try {
            const response = await axios.get('/api/export', {
                responseType: 'blob'
            });

            // Create a download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `accounted-backup-${new Date().toISOString().split('T')[0]}.json`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export data. Please try again.');
        }
    };

    const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);

            await axios.post('/api/import', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            onImportSuccess();
            alert('Data imported successfully!');
        } catch (error) {
            console.error('Import failed:', error);
            alert('Failed to import data. Please check the file format and try again.');
        }

        // Reset file input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="flex space-x-4">
            <button
                onClick={handleExport}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
                Export Data
            </button>
            <div>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImport}
                    accept=".json"
                    className="hidden"
                    id="import-file"
                />
                <label
                    htmlFor="import-file"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 cursor-pointer"
                >
                    Import Data
                </label>
            </div>
        </div>
    );
};

export default DataManagement; 