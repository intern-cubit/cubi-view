import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import WelcomePage from './components/WelcomePage';
import TrackEmployeePage from './components/TrackEmployeePage';
import LimitDevicePage from './components/LimitDevicePage';
import WebsiteWhitelistPage from './components/WebsiteWhitelistPage';
import InstallWhitelistPage from './components/InstallWhitelistPage';
import EmployeeReportPage from './components/EmployeeReportPage';
import SmtpConfigPage from './components/SmtpConfigPage';
import AboutUsPage from './components/AboutUsPage';
import PrivacyPolicyPage from './components/PrivacyPolicyPage';
import UpdateStatus from './components/UpdateStatus'; // Import the UpdateStatus component
import logo from './assets/cubiview-logo.png';
import { Key, Lock, User } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api'; // Changed to port 5000

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    const [currentPage, setCurrentPage] = useState('welcome');
    const [userInfo, setUserInfo] = useState(null);
    const [systemInfo, setSystemInfo] = useState({ system_id: 'Loading...', activation_key: 'Loading...' });

    // Fetch system info and activation key on component mount
    useEffect(() => {
        const fetchAppInfo = async () => {
            try {
                const [systemRes, activationRes] = await Promise.all([
                    fetch(`${API_BASE_URL}/system`),
                    fetch(`${API_BASE_URL}/activation`)
                ]);

                const systemData = await systemRes.json();
                console.log("System Data:", systemData);
                const activationData = await activationRes.json();

                setSystemInfo({
                    system_id: systemData.system_id,
                    activation_key: activationData.activation_key || '' // Ensure it's not null/undefined
                });
            } catch (error) {
                console.error("Error fetching initial app info:", error);
                // Set an error state or default values if API calls fail
                setSystemInfo({
                    system_id: 'N/A',
                    activation_key: 'Error'
                });
            }
        };

        fetchAppInfo();
    }, []);

    // Authentication part (KEEPING AS IS, AS NEW API.PY DOES NOT HAVE AUTH ROUTES)
    const authenticateAdmin = async (e) => {
        e.preventDefault();
        setLoginError('');
        setIsLoggingIn(true);

        try {
            const response = await fetch(`http://localhost:8000/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username, password: password }),
            });

            const data = await response.json();

            if (response.ok && data.token && data.user) {
                setUserInfo(data.user);
                setIsLoggedIn(true);
                setCurrentPage('welcome');
            } else {
                setLoginError(data.message || 'Login Failed, Invalid credentials.');
            }
        } catch (error) {
            console.error('Login error:', error);
            setLoginError('Connection Error. Could not connect to authentication server.');
        } finally {
            setIsLoggingIn(false);
        }
    };

    const askForgotPassword = () => {
        // Replaced window.alert with a custom modal/message box approach
        // For simplicity, I'm using a console log and a placeholder for a custom message box.
        // In a real app, you'd render a modal component here.
        console.log("Forgot password clicked. Implement custom modal for user confirmation.");
        // Example of how you might trigger a custom modal:
        // setShowForgotPasswordModal(true);

        const email = userInfo.email || '';
        if (!email) {
            // Replaced alert with console log and placeholder for custom message
            console.log("No email found in user info. Please log in first.");
            // You would show a user-friendly message here, e.g., a toast notification
            return;
        }
        // Instead of window.confirm, you'd show a custom confirmation modal
        // For now, directly call sendResetRequest for demonstration, but ideally,
        // this would be inside a confirmation modal's "confirm" action.
        sendResetRequest(email); // Pass email directly
    };

    const sendResetRequest = async (email) => {
        try {
            // THIS ROUTE IS NOT IN YOUR PROVIDED api.py.
            const response = await fetch(`http://localhost:8000/api/auth/forgot-password`, { // Assuming original auth service
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Replaced alert with console log and placeholder for custom message
                console.log("A reset link has been sent to your email.");
                // Show a success message to the user via a custom component (e.g., toast)
            } else {
                // Replaced alert with console log and placeholder for custom message
                console.log(data.message || "Failed to send reset email.");
                // Show an error message to the user via a custom component
            }
        } catch (error) {
            console.error('Forgot password error:', error);
            // Replaced alert with console log and placeholder for custom message
            console.log("Could not connect to server for password reset.");
            // Show a connection error message to the user
        }
    };
    // End of Authentication part

    const handlePageChange = (page) => {
        // Only allow navigation if activation key is present or if navigating to 'welcome'
        if (!isActivationKeyMissing || page === 'welcome') {
            setCurrentPage(page);
        } else {
            // Optionally, show a message that they need to activate first
            console.log("Please enter your activation key to unlock other features.");
            setCurrentPage('welcome'); // Force navigation back to welcome if they try to go elsewhere
        }
    };

    if (!isLoggedIn) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-100/20 via-indigo-100/20 to-purple-100/20"></div>
                <div className="relative z-10 w-full max-w-md">
                    <div className="bg-white/80 backdrop-blur-lg shadow-2xl rounded-2xl border border-white/20 overflow-hidden">
                        {/* Header Section */}
                        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 text-center">
                            <div className="mb-4">
                                <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-3">
                                    <img src={logo} alt="Cubi-View Logo" className="w-10 h-10 object-contain" />
                                </div>
                                <h2 className="text-2xl font-bold text-white">Welcome Back</h2>
                                <p className="text-blue-100 text-sm mt-1">Sign in to your admin account</p>
                            </div>
                        </div>

                        {/* Form Section */}
                        <div className="p-8">
                            <form onSubmit={authenticateAdmin} className="space-y-6">
                                {loginError && (
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
                                        <div className="flex-shrink-0">
                                            <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                            </svg>
                                        </div>
                                        <div className="text-red-700 text-sm font-medium">
                                            {loginError}
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-4">
                                    <div>
                                        <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
                                            Username
                                        </label>
                                        <div className="relative">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-black">
                                                <User size="20"/>
                                            </div>
                                            <input
                                                type="text"
                                                id="username"
                                                placeholder="Enter your username"
                                                value={username}
                                                onChange={(e) => setUsername(e.target.value)}
                                                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white/70 backdrop-blur-sm"
                                                required
                                                disabled={isLoggingIn}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                                            Password
                                        </label>
                                        <div className="relative">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <Lock size="20" className="text-gray-500" />
                                            </div>
                                            <input
                                                type="password"
                                                id="password"
                                                placeholder="Enter your password"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white/70 backdrop-blur-sm"
                                                required
                                                disabled={isLoggingIn}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={isLoggingIn}
                                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
                                >
                                    {isLoggingIn ? (
                                        <>
                                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                            <span>Logging in...</span>
                                        </>
                                    ) : (
                                        <>
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                                            </svg>
                                            <span>Sign In</span>
                                        </>
                                    )}
                                </button>

                                <div className="text-center">
                                    <button
                                        type="button"
                                        onClick={askForgotPassword}
                                        disabled={isLoggingIn}
                                        className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors duration-200 disabled:text-gray-400 disabled:cursor-not-allowed"
                                    >
                                        Forgot your password?
                                    </button>
                                </div>
                            </form>
                        </div>

                        {/* Footer */}
                        <div className="bg-gray-50 px-8 py-4 border-t border-gray-200">
                            <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                                </svg>
                                <span>Your connection is secure and encrypted</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Check if activation key is missing or 'N/A'
    const isActivationKeyMissing = !systemInfo.activation_key || systemInfo.activation_key === 'N/A' || systemInfo.activation_key === 'Error';

    return (
        <div className="app-container flex h-screen">
            {/* Pass isActivationKeyMissing to Sidebar to disable navigation items */}
            <Sidebar
                currentPage={currentPage}
                onPageChange={handlePageChange}
                isActivationKeyMissing={isActivationKeyMissing}
            />
            <div className="flex-grow p-6 overflow-y-auto bg-gray-50">
                <UpdateStatus />

                {/* Always render WelcomePage if it's the current page */}
                {currentPage === 'welcome' && (
                    <WelcomePage
                        systemId={systemInfo.system_id}
                        activationKey={systemInfo.activation_key}
                        userInfo={userInfo}
                        apiBaseUrl={API_BASE_URL}
                    />
                )}

                {/* Show activation required message only if key is missing AND user is not on welcome page */}
                {isActivationKeyMissing && currentPage !== 'welcome' && (
                    <div className="flex flex-col items-center justify-center h-full text-center p-4">
                        <h3 className="text-2xl font-semibold text-red-600 mb-4">Activation Required</h3>
                        <p className="text-gray-700 mb-6">
                            Please enter your activation key on the Welcome page to unlock all features.
                        </p>
                        <button
                            onClick={() => setCurrentPage('welcome')}
                            className="bg-primary-blue hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-primary-blue focus:ring-opacity-50 transition duration-300"
                        >
                            Go to Welcome Page
                        </button>
                    </div>
                )}

                {/* Render other pages only if activation key is present */}
                {!isActivationKeyMissing && (
                    <>
                        {currentPage === 'track' && <TrackEmployeePage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'limit' && <LimitDevicePage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'website' && <WebsiteWhitelistPage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'install_whitelist' && <InstallWhitelistPage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'report' && <EmployeeReportPage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'smtp' && <SmtpConfigPage apiBaseUrl={API_BASE_URL} />}
                        {currentPage === 'about' && <AboutUsPage />}
                        {currentPage === 'privacy' && <PrivacyPolicyPage />}
                    </>
                )}
            </div>
        </div>
    );
}

export default App;