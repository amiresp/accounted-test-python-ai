import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

interface User {
    id: string;
    username: string;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await axios.get('/api/auth/current-user');
                if (response.data) {
                    setUser(response.data);
                    // Store user data in localStorage
                    localStorage.setItem('user', JSON.stringify(response.data));
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                // Clear any stale data
                localStorage.removeItem('user');
            } finally {
                setLoading(false);
            }
        };

        // Check if we have stored user data
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                const parsedUser = JSON.parse(storedUser);
                setUser(parsedUser);
                // Verify the stored session is still valid
                checkAuth();
            } catch (error) {
                console.error('Error parsing stored user:', error);
                localStorage.removeItem('user');
            }
        } else {
            checkAuth();
        }
    }, []);

    const login = async (username: string, password: string) => {
        try {
            const response = await axios.post('/api/auth/login', { username, password });
            if (response.data.user) {
                setUser(response.data.user);
                // Store user data in localStorage
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await axios.get('/api/auth/logout');
            setUser(null);
            // Clear stored user data
            localStorage.removeItem('user');
        } catch (error) {
            console.error('Logout failed:', error);
            // Still clear local state even if server logout fails
            setUser(null);
            localStorage.removeItem('user');
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 