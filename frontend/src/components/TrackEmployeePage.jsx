import React, { useState, useEffect } from 'react';
import { 
  Keyboard, 
  MousePointer, 
  Clock, 
  Clipboard, 
  Printer, 
  Globe, 
  Activity, 
  Shield, 
  Camera, 
  Mic, 
  Video, 
  Download, 
  MapPin,
  CheckCircle,
  AlertCircle,
  Settings,
  Monitor
} from 'lucide-react';

const featureMapping = {
    "Keylogger": "Keylogger",
    "Keystroke / Word Count": "Keystroke / Word Count",
    "Mouse Click Count": "Mouse Click Count",
    "Mouse Movement Tracking": "Mouse Movement Tracking",
    "Active/Idle Time Detection": "Active/Idle Time Detection",
    "Clipboard Monitoring": "Clipboard Monitoring",
    "Print Job Monitoring": "Print Job Monitoring",
    "Browser History Logging": "Browser History Logging",
    "Application Usage Tracking": "Application Usage Tracking",
    "Detect Login / Logout + Screen Lock / Unlock": "Detect Login / Logout + Screen Lock / Unlock",
    "Capture Screenshots": "Capture Screenshots",
    "Capture Audio Clips": "Capture Audio Clips",
    "Capture Video Clips": "Capture Video Clips",
    "Installation / Uninstallation Logs": "Installation / Uninstallation Logs",
    "Laptop Geolocation (IP/GPS Based)": "Laptop Geolocation (IP/GPS Based)"
};

const featureIcons = {
    "Keylogger": Keyboard,
    "Keystroke / Word Count": Keyboard,
    "Mouse Click Count": MousePointer,
    "Mouse Movement Tracking": MousePointer,
    "Active/Idle Time Detection": Clock,
    "Clipboard Monitoring": Clipboard,
    "Print Job Monitoring": Printer,
    "Browser History Logging": Globe,
    "Application Usage Tracking": Activity,
    "Detect Login / Logout + Screen Lock / Unlock": Shield,
    "Capture Screenshots": Camera,
    "Capture Audio Clips": Mic,
    "Capture Video Clips": Video,
    "Installation / Uninstallation Logs": Download,
    "Laptop Geolocation (IP/GPS Based)": MapPin
};

const TrackEmployeePage = ({ apiBaseUrl }) => {
    const [config, setConfig] = useState({});
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('success');

    useEffect(() => {
        const loadConfig = async () => {
            try {
                const response = await fetch(`${apiBaseUrl}/config`);
                if (!response.ok) throw new Error('Failed to load config');
                const data = await response.json();
                setConfig(data);
            } catch (error) {
                console.error('Error loading config:', error);
                setMessage('Failed to load monitoring configuration.');
                setMessageType('error');
            }
        };
        loadConfig();
    }, [apiBaseUrl]);

    const toggleFeature = async (featureKey, currentStatus) => {
        const newStatus = !currentStatus;
        setConfig(prev => ({ ...prev, [featureKey]: newStatus }));

        try {
            const response = await fetch(`${apiBaseUrl}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ features: { [featureKey]: newStatus } }),
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Failed to save config');
            }
            setMessage(`'${featureKey}' successfully ${newStatus ? 'enabled' : 'disabled'}.`);
            setMessageType('success');
        } catch (error) {
            console.error('Error saving config:', error);
            setMessage(`Failed to update '${featureKey}'.`);
            setMessageType('error');
            setConfig(prev => ({ ...prev, [featureKey]: currentStatus }));
        }
    };

    const getMessageIcon = () => {
        switch (messageType) {
            case 'success': return <CheckCircle className="w-5 h-5" />;
            case 'error': return <AlertCircle className="w-5 h-5" />;
            case 'warning': return <AlertCircle className="w-5 h-5" />;
            case 'info': return <AlertCircle className="w-5 h-5" />;
            default: return null;
        }
    };

    const getMessageClasses = () => {
        switch (messageType) {
            case 'success': return 'bg-emerald-50 text-emerald-800 border-emerald-200';
            case 'error': return 'bg-red-50 text-red-800 border-red-200';
            case 'warning': return 'bg-amber-50 text-amber-800 border-amber-200';
            case 'info': return 'bg-blue-50 text-blue-800 border-blue-200';
            default: return '';
        }
    };

    const enabledCount = Object.values(config).filter(Boolean).length;
    const totalCount = Object.keys(featureMapping).length;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
            <div className="container mx-auto px-4 py-8">
                {/* Header Section */}
                <div className="text-center mb-12">
                    <div className="flex justify-center items-center mb-6">
                        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-2xl shadow-lg">
                            <Monitor className="w-12 h-12 text-white" />
                        </div>
                    </div>
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Employee Tracker</h1>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        Customize your monitoring preferences with our intuitive configuration panel
                    </p>
                    
                    {/* Stats Bar */}
                    <div className="flex justify-center mt-8">
                        <div className="bg-white rounded-full px-6 py-3 shadow-lg border border-gray-100">
                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2">
                                    <Settings className="w-5 h-5 text-blue-600" />
                                    <span className="text-gray-700 font-medium">
                                        {enabledCount} of {totalCount} features enabled
                                    </span>
                                </div>
                                <div className="w-px h-6 bg-gray-300"></div>
                                <div className="w-24 bg-gray-200 rounded-full h-2">
                                    <div 
                                        className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${(enabledCount / totalCount) * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Message Alert */}
                {message && (
                    <div className={`mb-8 p-4 border rounded-xl ${getMessageClasses()} shadow-sm`}>
                        <div className="flex items-center space-x-3">
                            {getMessageIcon()}
                            <span className="font-medium">{message}</span>
                        </div>
                    </div>
                )}

                {/* Features Grid */}
                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                    <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-8 py-6 border-b border-gray-100">
                        <h2 className="text-2xl font-semibold text-gray-900">Monitoring Features</h2>
                        <p className="text-gray-600 mt-2">Toggle features on or off based on your requirements</p>
                    </div>
                    
                    <div className="p-8">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {Object.entries(featureMapping).map(([displayText, featureKey], index) => {
                                const IconComponent = featureIcons[featureKey] || Activity;
                                const isEnabled = config[featureKey] || false;
                                
                                return (
                                    <div 
                                        key={index} 
                                        className={`
                                            group relative p-6 rounded-xl border-2 transition-all duration-300 cursor-pointer
                                            ${isEnabled 
                                                ? 'border-blue-200 bg-blue-50 hover:border-blue-300 hover:bg-blue-100' 
                                                : 'border-gray-200 bg-gray-50 hover:border-gray-300 hover:bg-gray-100'
                                            }
                                        `}
                                        onClick={() => toggleFeature(featureKey, isEnabled)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-4">
                                                <div className={`
                                                    p-3 rounded-lg transition-colors duration-300
                                                    ${isEnabled 
                                                        ? 'bg-blue-100 text-blue-600' 
                                                        : 'bg-gray-200 text-gray-500'
                                                    }
                                                `}>
                                                    <IconComponent className="w-6 h-6" />
                                                </div>
                                                <div>
                                                    <h3 className="font-semibold text-gray-900 text-lg">
                                                        {displayText}
                                                    </h3>
                                                    <p className={`text-sm mt-1 ${isEnabled ? 'text-blue-600' : 'text-gray-500'}`}>
                                                        {isEnabled ? 'Active' : 'Inactive'}
                                                    </p>
                                                </div>
                                            </div>
                                            
                                            {/* Toggle Switch */}
                                            <label className="relative inline-flex items-center cursor-pointer">
                                                <input
                                                    type="checkbox"
                                                    className="sr-only peer"
                                                    checked={isEnabled}
                                                    onChange={() => toggleFeature(featureKey, isEnabled)}
                                                />
                                                <div className={`
                                                    relative w-14 h-8 rounded-full peer transition-colors duration-300
                                                    ${isEnabled 
                                                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500' 
                                                        : 'bg-gray-300'
                                                    }
                                                `}>
                                                    <div className={`
                                                        absolute top-1 left-1 bg-white w-6 h-6 rounded-full shadow-md
                                                        transition-transform duration-300 ease-in-out
                                                        ${isEnabled ? 'translate-x-6' : 'translate-x-0'}
                                                    `}>
                                                    </div>
                                                </div>
                                            </label>
                                        </div>
                                        
                                        {/* Hover effect overlay */}
                                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/5 to-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center mt-12">
                    <p className="text-gray-500">
                        Changes are saved automatically. Configure features according to your monitoring needs.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default TrackEmployeePage;