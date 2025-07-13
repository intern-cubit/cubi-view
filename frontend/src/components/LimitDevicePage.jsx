import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Puzzle, 
  Usb, 
  EyeOff, 
  CheckCircle, 
  XCircle, 
  Camera, 
  Copy, 
  Download, 
  ShieldCheck, 
  Bug, 
  Clock, 
  Coffee,
  Settings,
  AlertTriangle,
  CheckCircle2,
  X
} from 'lucide-react';

const featureMapping = {
  "VPN Detection & Blocking": {
    key: "VPN Detection & Blocking",
    icon: Shield,
    description: "Detect and block VPN connections",
    category: "Security"
  },
  "Chrome Extension Restrictions": {
    key: "Chrome Extension Restrictions",
    icon: Puzzle,
    description: "Control browser extension usage",
    category: "Browser"
  },
  "USB Port Access Control": {
    key: "USB Port Access Control",
    icon: Usb,
    description: "Manage USB device connections",
    category: "Hardware"
  },
  "Incognito Mode Blocking": {
    key: "Incognito Mode Blocking",
    icon: EyeOff,
    description: "Prevent private browsing mode",
    category: "Browser"
  },
  "Website Whitelisting": {
    key: "Website Whitelisting",
    icon: CheckCircle,
    description: "Allow access to specific websites only",
    category: "Web Access"
  },
  "Website Blocking": {
    key: "Website Blocking",
    icon: XCircle,
    description: "Block access to specific websites",
    category: "Web Access"
  },
  "Screenshot / Snipping Tool Prevention": {
    key: "Screenshot / Snipping Tool Prevention",
    icon: Camera,
    description: "Prevent screen capture tools",
    category: "Security"
  },
  "Copy-Paste Enable / Disable": {
    key: "Copy-Paste Enable / Disable",
    icon: Copy,
    description: "Control clipboard functionality",
    category: "System"
  },
  "Download Enable / Disable": {
    key: "Download Enable / Disable",
    icon: Download,
    description: "Control file download permissions",
    category: "System"
  },
  // "Built-in Ad Blocker": {
  //   key: "Built-in Ad Blocker",
  //   icon: ShieldCheck,
  //   description: "Block advertisements and trackers",
  //   category: "Browser"
  // },
  // "Custom Antivirus & Spam Link Detection": {
  //   key: "Custom Antivirus & Spam Link Detection",
  //   icon: Bug,
  //   description: "Detect malicious content and links",
  //   category: "Security"
  // },
  "Internet / Screen Time Limits": {
    key: "Internet / Screen Time Limits",
    icon: Clock,
    description: "Set usage time restrictions",
    category: "Time Management"
  },
  "Lunch Break Mode": {
    key: "Lunch Break Mode",
    icon: Coffee,
    description: "Temporary access relaxation",
    category: "Time Management"
  }
};

const LimitDevicePage = ({ apiBaseUrl }) => {
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
        setMessage('Failed to load device limitation configuration.');
        setMessageType('error');
      }
    };
    loadConfig();
  }, [apiBaseUrl]);

  // Effect to handle mutual exclusivity for Website Whitelisting and Website Blocking
  useEffect(() => {
    const whitelistOn = config["Website Whitelisting"];
    const blocklistOn = config["Website Blocking"];

    if (whitelistOn && blocklistOn) {
      setConfig(prev => ({ ...prev, "Website Blocking": false }));
      setMessage("Website Whitelisting and Website Blocking cannot be enabled simultaneously. Website Blocking was disabled.");
      setMessageType("warning");
    } else if (config["Website Blocking"] && config["Website Whitelisting"] === undefined) {
       setConfig(prev => ({ ...prev, "Website Whitelisting": false }));
    } else if (config["Website Whitelisting"] && config["Website Blocking"] === undefined) {
        setConfig(prev => ({ ...prev, "Website Blocking": false }));
    }
  }, [config["Website Whitelisting"], config["Website Blocking"]]);

  const toggleFeature = async (featureKey, currentStatus) => {
    let newStatus = !currentStatus;
    let updates = { [featureKey]: newStatus };
    let successMessage = `'${featureKey}' successfully ${newStatus ? 'enabled' : 'disabled'}.`;
    let errorMessage = `Failed to update '${featureKey}'.`;

    // Handle mutual exclusivity for Website Whitelisting and Website Blocking
    if (featureKey === "Website Whitelisting" && newStatus) {
      if (config["Website Blocking"]) {
        updates["Website Blocking"] = false;
        successMessage += " Website Blocking was disabled.";
      }
    } else if (featureKey === "Website Blocking" && newStatus) {
      if (config["Website Whitelisting"]) {
        updates["Website Whitelisting"] = false;
        successMessage += " Website Whitelisting was disabled.";
      }
    }

    setConfig(prev => ({ ...prev, ...updates }));

    try {
      const response = await fetch(`${apiBaseUrl}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: updates }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.message || 'Failed to save config');
      }
      setMessage(successMessage);
      setMessageType('success');
    } catch (error) {
      console.error('Error saving config:', error);
      setMessage(errorMessage);
      setMessageType('error');
      const revertedUpdates = {};
      for (const key in updates) {
        revertedUpdates[key] = config[key];
      }
      setConfig(prev => ({ ...prev, ...revertedUpdates }));
    }
  };

  const getMessageIcon = () => {
    switch (messageType) {
      case 'success': return <CheckCircle2 className="w-5 h-5" />;
      case 'error': return <X className="w-5 h-5" />;
      case 'warning': return <AlertTriangle className="w-5 h-5" />;
      case 'info': return <Settings className="w-5 h-5" />;
      default: return null;
    }
  };

  const getMessageClasses = () => {
    switch (messageType) {
      case 'success': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'error': return 'bg-red-50 text-red-700 border-red-200';
      case 'warning': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'info': return 'bg-blue-50 text-blue-700 border-blue-200';
      default: return '';
    }
  };

  // Group features by category
  const groupedFeatures = Object.entries(featureMapping).reduce((acc, [displayText, featureData]) => {
    if (!acc[featureData.category]) {
      acc[featureData.category] = [];
    }
    acc[featureData.category].push({ displayText, ...featureData });
    return acc;
  }, {});

  const categoryColors = {
    "Security": "bg-red-500",
    "Browser": "bg-blue-500",
    "Hardware": "bg-purple-500",
    "Web Access": "bg-green-500",
    "System": "bg-orange-500",
    "Time Management": "bg-indigo-500"
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-full">
              <Settings className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Device Security Settings</h1>
          <p className="text-gray-600 text-lg">Configure device limitations and security features</p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 border rounded-lg flex items-center space-x-3 ${getMessageClasses()}`}>
            {getMessageIcon()}
            <span className="font-medium">{message}</span>
          </div>
        )}

        {/* Features Grid */}
        <div className="space-y-8">
          {Object.entries(groupedFeatures).map(([category, features]) => (
            <div key={category} className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* Category Header */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${categoryColors[category]}`}></div>
                  <h2 className="text-xl font-semibold text-gray-800">{category}</h2>
                  <span className="text-sm text-gray-500">({features.length} features)</span>
                </div>
              </div>

              {/* Features List */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {features.map((feature, index) => {
                    const IconComponent = feature.icon;
                    const isEnabled = config[feature.key] || false;
                    
                    return (
                      <div
                        key={index}
                        className={`relative bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border-2 transition-all duration-300 hover:shadow-md cursor-pointer ${
                          isEnabled 
                            ? 'border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => toggleFeature(feature.key, isEnabled)}
                      >
                        {/* Feature Icon and Status */}
                        <div className="flex items-start justify-between mb-4">
                          <div className={`p-3 rounded-lg ${
                            isEnabled ? 'bg-blue-100' : 'bg-gray-100'
                          }`}>
                            <IconComponent className={`w-6 h-6 ${
                              isEnabled ? 'text-blue-600' : 'text-gray-600'
                            }`} />
                          </div>
                          
                          {/* Toggle Switch */}
                          <div className="relative">
                            <div
                              className={`w-12 h-6 rounded-full transition-all duration-300 ${
                                isEnabled 
                                  ? 'bg-gradient-to-r from-blue-500 to-blue-600' 
                                  : 'bg-gray-300'
                              }`}
                            >
                              <div
                                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-300 ${
                                  isEnabled ? 'translate-x-6' : 'translate-x-0'
                                }`}
                              />
                            </div>
                          </div>
                        </div>

                        {/* Feature Details */}
                        <div>
                          <h3 className="font-semibold text-gray-800 mb-2 leading-tight">
                            {feature.displayText}
                          </h3>
                          <p className="text-sm text-gray-600 mb-3">
                            {feature.description}
                          </p>
                          
                          {/* Status Badge */}
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              isEnabled 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {isEnabled ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                        </div>

                        {/* Hover Effect Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-purple-500/0 hover:from-blue-500/5 hover:to-purple-500/5 rounded-xl transition-all duration-300" />
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500">
          <p className="text-sm">
            Configure these settings to enhance device security and control user access.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LimitDevicePage;