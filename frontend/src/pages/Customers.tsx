import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Customer {
    id: string;
    first_name: string;
    last_name: string;
    company: string;
    mobile: string;
    address: string;
    credit_cards: string[];
    bank_accounts: string[];
}

const Customers: React.FC = () => {
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
    const [newCustomer, setNewCustomer] = useState({
        first_name: '',
        last_name: '',
        company: '',
        mobile: '',
        address: '',
        credit_cards: [''],
        bank_accounts: ['']
    });

    useEffect(() => {
        fetchCustomers();
    }, []);

    const fetchCustomers = async () => {
        try {
            const response = await axios.get('/api/customers');
            setCustomers(response.data);
        } catch (err) {
            setError('Failed to load customers');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingCustomer) {
                await axios.put(`/api/customers/${editingCustomer.id}`, newCustomer);
            } else {
                await axios.post('/api/customers', newCustomer);
            }
            setShowModal(false);
            setEditingCustomer(null);
            setNewCustomer({
                first_name: '',
                last_name: '',
                company: '',
                mobile: '',
                address: '',
                credit_cards: [''],
                bank_accounts: ['']
            });
            fetchCustomers();
        } catch (err) {
            setError(editingCustomer ? 'Failed to update customer' : 'Failed to create customer');
        }
    };

    const handleEdit = (customer: Customer) => {
        setEditingCustomer(customer);
        setNewCustomer({
            first_name: customer.first_name,
            last_name: customer.last_name,
            company: customer.company,
            mobile: customer.mobile,
            address: customer.address,
            credit_cards: customer.credit_cards.length > 0 ? customer.credit_cards : [''],
            bank_accounts: customer.bank_accounts.length > 0 ? customer.bank_accounts : ['']
        });
        setShowModal(true);
    };

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this customer?')) {
            try {
                await axios.delete(`/api/customers/${id}`);
                fetchCustomers();
            } catch (err) {
                setError('Failed to delete customer');
            }
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingCustomer(null);
        setNewCustomer({
            first_name: '',
            last_name: '',
            company: '',
            mobile: '',
            address: '',
            credit_cards: [''],
            bank_accounts: ['']
        });
    };

    const addCreditCard = () => {
        setNewCustomer({
            ...newCustomer,
            credit_cards: [...newCustomer.credit_cards, '']
        });
    };

    const addBankAccount = () => {
        setNewCustomer({
            ...newCustomer,
            bank_accounts: [...newCustomer.bank_accounts, '']
        });
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Customers</h2>
                <button
                    onClick={() => setShowModal(true)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                >
                    Add Customer
                </button>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Company</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mobile</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Address</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {customers.map((customer) => (
                            <tr key={customer.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {customer.first_name} {customer.last_name}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.company}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.mobile}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.address}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    <button
                                        onClick={() => handleEdit(customer)}
                                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(customer.id)}
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
                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            {editingCustomer ? 'Edit Customer' : 'Add New Customer'}
                        </h3>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">First Name</label>
                                    <input
                                        type="text"
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newCustomer.first_name}
                                        onChange={(e) => setNewCustomer({ ...newCustomer, first_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">Last Name</label>
                                    <input
                                        type="text"
                                        required
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={newCustomer.last_name}
                                        onChange={(e) => setNewCustomer({ ...newCustomer, last_name: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Company</label>
                                <input
                                    type="text"
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    value={newCustomer.company}
                                    onChange={(e) => setNewCustomer({ ...newCustomer, company: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Mobile</label>
                                <input
                                    type="tel"
                                    required
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    value={newCustomer.mobile}
                                    onChange={(e) => setNewCustomer({ ...newCustomer, mobile: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Address</label>
                                <textarea
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    value={newCustomer.address}
                                    onChange={(e) => setNewCustomer({ ...newCustomer, address: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Credit Cards</label>
                                {newCustomer.credit_cards.map((card, index) => (
                                    <input
                                        key={index}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={card}
                                        onChange={(e) => {
                                            const newCards = [...newCustomer.credit_cards];
                                            newCards[index] = e.target.value;
                                            setNewCustomer({ ...newCustomer, credit_cards: newCards });
                                        }}
                                    />
                                ))}
                                <button
                                    type="button"
                                    onClick={addCreditCard}
                                    className="mt-2 text-sm text-indigo-600 hover:text-indigo-900"
                                >
                                    + Add Credit Card
                                </button>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Bank Accounts</label>
                                {newCustomer.bank_accounts.map((account, index) => (
                                    <input
                                        key={index}
                                        type="text"
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                        value={account}
                                        onChange={(e) => {
                                            const newAccounts = [...newCustomer.bank_accounts];
                                            newAccounts[index] = e.target.value;
                                            setNewCustomer({ ...newCustomer, bank_accounts: newAccounts });
                                        }}
                                    />
                                ))}
                                <button
                                    type="button"
                                    onClick={addBankAccount}
                                    className="mt-2 text-sm text-indigo-600 hover:text-indigo-900"
                                >
                                    + Add Bank Account
                                </button>
                            </div>
                            <div className="flex justify-end space-x-3">
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
                                    {editingCustomer ? 'Update' : 'Create'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Customers; 