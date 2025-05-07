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

interface DashboardData {
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
    topCustomers: {
        id: string;
        name: string;
        revenue: number;
    }[];
}

const Dashboard: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Calculate date range for the last 30 days
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - 30);

                const [profitLoss, incomeExpenses, topCustomers] = await Promise.all([
                    axios.get('http://localhost:5000/api/reports/profit-loss'),
                    axios.get('http://localhost:5000/api/reports/income-expenses', {
                        params: {
                            start_date: startDate.toISOString(),
                            end_date: endDate.toISOString()
                        }
                    }),
                    axios.get('http://localhost:5000/api/reports/top-customers'),
                ]);

                setData({
                    profitLoss: profitLoss.data,
                    incomeExpenses: incomeExpenses.data,
                    topCustomers: topCustomers.data,
                });
            } catch (err) {
                setError('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    if (!data) {
        return null;
    }

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Income
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.total_income.toFixed(2)}
                        </dd>
                    </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Expenses
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.total_expenses.toFixed(2)}
                        </dd>
                    </div>
                </div>

                <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                        <dt className="text-sm font-medium text-gray-500 truncate">
                            Net Profit
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900">
                            ${data.profitLoss.net_profit.toFixed(2)}
                        </dd>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Income vs Expenses
                </h3>
                <div className="h-80">
                    <Line
                        data={data.incomeExpenses}
                        options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                },
                            },
                        }}
                    />
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Top Customers
                </h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Customer
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Revenue
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {data.topCustomers.map((customer) => (
                                <tr key={customer.id}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {customer.name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        ${customer.revenue.toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 