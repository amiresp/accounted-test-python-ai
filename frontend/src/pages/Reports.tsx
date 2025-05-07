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
    ChartOptions,
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
    profitLoss: {
        total_income: number;
        total_expenses: number;
        net_profit: number;
    };
    incomeExpenses: {
        labels: string[];
        datasets: {
            label: string;
            data: number[];
        }[];
    };
}

const Reports: React.FC = () => {
    const [data, setData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [profitLoss, incomeExpenses] = await Promise.all([
                    axios.get('/api/reports/profit-loss'),
                    axios.get('/api/reports/income-expenses'),
                ]);

                setData({
                    profitLoss: profitLoss.data,
                    incomeExpenses: {
                        ...incomeExpenses.data,
                        datasets: incomeExpenses.data.datasets.map((dataset: any, index: number) => ({
                            ...dataset,
                            borderColor: index === 0 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)',
                            backgroundColor: index === 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)',
                            tension: 0.1,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                        })),
                    },
                });
            } catch (err) {
                setError('Failed to load reports');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!data) return null;

    const chartOptions: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value) {
                        return `$${Number(value).toFixed(2)}`;
                    }
                }
            }
        },
        plugins: {
            legend: {
                position: 'top' as const,
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const label = context.dataset.label || '';
                        const value = context.parsed.y;
                        return `${label}: $${value.toFixed(2)}`;
                    }
                }
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500">Total Income</dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.total_income.toFixed(2)}
                        </dd>
                    </div>
                </div>
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500">Total Expenses</dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.total_expenses.toFixed(2)}
                        </dd>
                    </div>
                </div>
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500">Net Profit</dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.net_profit.toFixed(2)}
                        </dd>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Income vs Expenses</h3>
                <div className="h-80">
                    <Line data={data.incomeExpenses} options={chartOptions} />
                </div>
            </div>
        </div>
    );
};

export default Reports; 