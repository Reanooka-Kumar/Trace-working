import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Activity, Shield, Users, User, LogOut, Settings } from 'lucide-react';

const Navbar = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const token = localStorage.getItem('token');
        setIsLoggedIn(!!token);
        setShowProfileMenu(false);
    }, [location]);

    const handleSignOut = () => {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        navigate('/login');
    };

    return (
        <nav className="fixed top-0 w-full z-50 p-4">
            <div className="max-w-7xl mx-auto glass-panel px-6 py-3 flex justify-between items-center">
                <Link to="/" className="flex items-center space-x-2">
                    <Activity className="w-8 h-8 text-primary" />
                    <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                        TRACE
                    </span>
                </Link>

                <div className="hidden md:flex space-x-8 text-sm font-medium text-gray-300">
                    <Link to="/search" className="hover:text-primary transition-colors flex items-center gap-2">
                        <Users className="w-4 h-4" /> Find Teams
                    </Link>
                    <Link to="/dashboard" className="hover:text-primary transition-colors flex items-center gap-2">
                        <Shield className="w-4 h-4" /> Dashboard
                    </Link>
                </div>

                <div className="flex items-center space-x-4">
                    {isLoggedIn ? (
                        <div className="relative">
                            <button
                                onClick={() => setShowProfileMenu(!showProfileMenu)}
                                className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-white font-bold hover:scale-105 transition-transform"
                            >
                                <User className="w-5 h-5" />
                            </button>

                            {showProfileMenu && (
                                <div className="absolute right-0 mt-2 w-48 bg-dark-light border border-white/10 rounded-xl shadow-xl overflow-hidden py-1 backdrop-blur-xl">
                                    <Link
                                        to="/profile"
                                        className="flex items-center gap-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
                                    >
                                        <Settings className="w-4 h-4" /> Edit Profile
                                    </Link>
                                    <button
                                        onClick={handleSignOut}
                                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors text-left"
                                    >
                                        <LogOut className="w-4 h-4" /> Sign Out
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <Link to="/login" className="px-4 py-2 rounded-lg bg-primary/20 text-primary border border-primary/50 hover:bg-primary/30 transition-all font-semibold backdrop-blur-md">
                            Sign In
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
