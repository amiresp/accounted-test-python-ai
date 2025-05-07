import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DataManagement from '../components/DataManagement';

interface Invoice {
    id: string;
    customer_id: string;
    customer_name: string;
    date: string;
    due_date: string;
    payment_date?: string;
    payment_info?: string;
    total: number;
    status: 'pending' | 'paid' | 'overdue' | 'cancelled';
    items: InvoiceItem[];
}

interface InvoiceItem {
    description: string;
    quantity: number;
    unit_price: number;
    amount: number;
}

interface Customer {
    id: string;
    first_name: string;
    last_name: string;
}

const Invoices: React.FC = () => {
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null);
    const [newInvoice, setNewInvoice] = useState<{
        customer_id: string;
        date: string;
        due_date: string;
        payment_date: string;
        payment_info: string;
        status: Invoice['status'];
        items: { description: string; quantity: number; unit_price: number; amount: number; }[];
    }>({
        customer_id: '',
        date: new Date().toISOString().split('T')[0],
        due_date: '',
        payment_date: '',
        payment_info: '',
        status: 'pending',
        items: [{ description: '', quantity: 1, unit_price: 0, amount: 0 }]
    });

    useEffect(() => {
        fetchInvoices();
        fetchCustomers();
    }, []);

    const fetchInvoices = async () => {
        try {
            const response = await axios.get('/api/invoices');
            setInvoices(response.data);
        } catch (err) {
            setError('Failed to load invoices');
        } finally {
            setLoading(false);
        }
    };

    const fetchCustomers = async () => {
        try {
            const response = await axios.get('/api/customers');
            setCustomers(response.data);
        } catch (err) {
            setError('Failed to load customers');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingInvoice) {
                await axios.put(`/api/invoices/${editingInvoice.id}`, newInvoice);
            } else {
                await axios.post('/api/invoices', newInvoice);
            }
            setShowModal(false);
            setEditingInvoice(null);
            setNewInvoice({
                customer_id: '',
                date: new Date().toISOString().split('T')[0],
                due_date: '',
                payment_date: '',
                payment_info: '',
                status: 'pending',
                items: [{ description: '', quantity: 1, unit_price: 0, amount: 0 }]
            });
            fetchInvoices();
        } catch (err) {
            setError(editingInvoice ? 'Failed to update invoice' : 'Failed to create invoice');
        }
    };

    const handleEdit = (invoice: Invoice) => {
        setEditingInvoice(invoice);
        setNewInvoice({
            customer_id: invoice.customer_id,
            date: invoice.date,
            due_date: invoice.due_date,
            payment_date: invoice.payment_date || '',
            payment_info: invoice.payment_info || '',
            status: invoice.status,
            items: invoice.items.map(item => ({
                description: item.description,
                quantity: item.quantity,
                unit_price: item.unit_price,
                amount: item.amount
            }))
        });
        setShowModal(true);
    };

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this invoice?')) {
            try {
                await axios.delete(`/api/invoices/${id}`);
                fetchInvoices();
            } catch (err) {
                setError('Failed to delete invoice');
            }
        }
    };

    const handleStatusChange = async (id: string, newStatus: Invoice['status']) => {
        try {
            const invoice = invoices.find(inv => inv.id === id);
            if (!invoice) return;

            await axios.put(`/api/invoices/${id}`, {
                ...invoice,
                status: newStatus,
                payment_date: newStatus === 'paid' ? new Date().toISOString().split('T')[0] : invoice.payment_date
            });
            fetchInvoices();
        } catch (err) {
            setError('Failed to update invoice status');
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingInvoice(null);
        setNewInvoice({
            customer_id: '',
            date: new Date().toISOString().split('T')[0],
            due_date: '',
            payment_date: '',
            payment_info: '',
            status: 'pending',
            items: [{ description: '', quantity: 1, unit_price: 0, amount: 0 }]
        });
    };

    const addItem = () => {
        setNewInvoice({
            ...newInvoice,
            items: [...newInvoice.items, { description: '', quantity: 1, unit_price: 0, amount: 0 }]
        });
    };

    const updateItem = (index: number, field: keyof InvoiceItem, value: string | number) => {
        const newItems = [...newInvoice.items];
        newItems[index] = {
            ...newItems[index],
            [field]: value,
            amount: field === 'quantity' || field === 'unit_price'
                ? Number(newItems[index].quantity) * Number(newItems[index].unit_price)
                : newItems[index].amount
        };
        setNewInvoice({ ...newInvoice, items: newItems });
    };

    const getStatusColor = (status: Invoice['status']) => {
        switch (status) {
            case 'paid':
                return 'bg-green-100 text-green-800';
            case 'overdue':
                return 'bg-red-100 text-red-800';
            case 'cancelled':
                return 'bg-gray-100 text-gray-800';
            default:
                return 'bg-yellow-100 text-yellow-800';
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Invoices</h2>
                <div className="flex items-center space-x-4">
                    <DataManagement onImportSuccess={fetchInvoices} />
                    <button
                        onClick={() => setShowModal(true)}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                    >
                        Create Invoice
                    </button>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {invoices.map((invoice) => (
                            <tr key={invoice.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {invoice.customer_name}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{invoice.date}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{invoice.due_date}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{invoice.payment_date || '-'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${invoice.total.toFixed(2)}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <select
                                        value={invoice.status}
                                        onChange={(e) => handleStatusChange(invoice.id, e.target.value as Invoice['status'])}
                                        className={`text-sm rounded-full px-2 py-1 font-semibold ${getStatusColor(invoice.status)}`}
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="paid">Paid</option>
                                        <option value="overdue">Overdue</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => handleEdit(invoice)}
                                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(invoice.id)}
                                        className="text-red-600 hover:text-red-900"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
                    <div className="bg-white rounded-lg p-6 max-w-4xl w-full">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            {editingInvoice ? 'Edit Invoice' : 'Create New Invoice'}
                        </h3>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Customer</label>
                                    <select
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newInvoice.customer_id}
                                        onChange={(e) => setNewInvoice({ ...newInvoice, customer_id: e.target.value })}
                                    >
                                        <option value="">Select Customer</option>
                                        {customers.map((customer) => (
                                            <option key={customer.id} value={customer.id}>
                                                {customer.first_name} {customer.last_name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Date</label>
                                    <input
                                        type="date"
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newInvoice.date}
                                        onChange={(e) => setNewInvoice({ ...newInvoice, date: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Due Date</label>
                                    <input
                                        type="date"
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newInvoice.due_date}
                                        onChange={(e) => setNewInvoice({ ...newInvoice, due_date: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Status</label>
                                    <select
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newInvoice.status}
                                        onChange={(e) => setNewInvoice({ ...newInvoice, status: e.target.value as Invoice['status'] })}
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="paid">Paid</option>
                                        <option value="overdue">Overdue</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
                                </div>
                                {newInvoice.status === 'paid' && (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Payment Date</label>
                                            <input
                                                type="date"
                                                required
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                value={newInvoice.payment_date}
                                                onChange={(e) => setNewInvoice({ ...newInvoice, payment_date: e.target.value })}
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">Payment Info</label>
                                            <input
                                                type="text"
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                value={newInvoice.payment_info}
                                                onChange={(e) => setNewInvoice({ ...newInvoice, payment_info: e.target.value })}
                                                placeholder="e.g., Check #1234, Bank Transfer"
                                            />
                                        </div>
                                    </>
                                )}
                            </div>

                            <div className="mt-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h4 className="text-lg font-medium text-gray-900">Items</h4>
                                    <button
                                        type="button"
                                        onClick={addItem}
                                        className="text-sm text-indigo-600 hover:text-indigo-900"
                                    >
                                        + Add Item
                                    </button>
                                </div>
                                <div className="space-y-4">
                                    {newInvoice.items.map((item, index) => (
                                        <div key={index} className="grid grid-cols-4 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Description</label>
                                                <input
                                                    type="text"
                                                    required
                                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                    value={item.description}
                                                    onChange={(e) => updateItem(index, 'description', e.target.value)}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Quantity</label>
                                                <input
                                                    type="number"
                                                    required
                                                    min="1"
                                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                    value={item.quantity}
                                                    onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value))}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Unit Price</label>
                                                <input
                                                    type="number"
                                                    required
                                                    min="0"
                                                    step="0.01"
                                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                                    value={item.unit_price}
                                                    onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value))}
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700">Amount</label>
                                                <input
                                                    type="number"
                                                    readOnly
                                                    className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm"
                                                    value={item.amount}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={handleCloseModal}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md"
                                >
                                    {editingInvoice ? 'Update' : 'Create'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Invoices; 