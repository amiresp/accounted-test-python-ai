import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

interface ReportData {
    income: number;
    expenses: number;
    net: number;
    start_date: string;
    end_date: string;
    invoice_count: number;
    message?: string;
}

const Dashboard: React.FC = () => {
    const [reportData, setReportData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await axios.get('/api/reports/income-expenses');
                setReportData(response.data);
                setError(null);
            } catch (err) {
                console.error('Error fetching report data:', err);
                setError('Failed to load report data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="p-4">
                <div className="animate-pulse">
                    <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="h-32 bg-gray-200 rounded"></div>
                        <div className="h-32 bg-gray-200 rounded"></div>
                        <div className="h-32 bg-gray-200 rounded"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4">
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

            {reportData?.message && (
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded mb-4">
                    {reportData.message}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500 text-sm font-medium">Total Income</h3>
                    <p className="text-2xl font-bold text-green-600">
                        ${reportData?.income.toFixed(2) || '0.00'}
                    </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500 text-sm font-medium">Total Expenses</h3>
                    <p className="text-2xl font-bold text-red-600">
                        ${reportData?.expenses.toFixed(2) || '0.00'}
                    </p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-gray-500 text-sm font-medium">Net Profit</h3>
                    <p className={`text-2xl font-bold ${reportData?.net && reportData.net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${reportData?.net.toFixed(2) || '0.00'}
                    </p>
                </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold mb-4">Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <p className="text-gray-600">Period</p>
                        <p className="font-medium">
                            {reportData?.start_date ? new Date(reportData.start_date).toLocaleDateString() : 'N/A'} -
                            {reportData?.end_date ? new Date(reportData.end_date).toLocaleDateString() : 'N/A'}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Total Invoices</p>
                        <p className="font-medium">{reportData?.invoice_count || 0}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 