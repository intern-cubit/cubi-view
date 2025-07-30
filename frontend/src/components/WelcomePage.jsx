import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Server, 
  Key, 
  Play, 
  Square, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info,
  Activity,
  Settings
} from 'lucide-react';

const WelcomePage = ({ systemId, activationKey, userInfo, apiBaseUrl }) => {
  const [currentActivationKey, setCurrentActivationKey] = useState(activationKey);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success'); // success, error, warning, info
  const [monitoringStatus, setMonitoringStatus] = useState(false);
  const [isCheckingUpdate, setIsCheckingUpdate] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [localVersion, setLocalVersion] = useState('Loading...');

  // Get app version from Electron
  useEffect(() => {
    const getAppVersion = async () => {
      try {
        console.log('Attempting to get app version from Electron...');
        if (window.electronAPI && window.electronAPI.getAppVersion) {
          console.log('electronAPI.getAppVersion is available');
          const version = await window.electronAPI.getAppVersion();
          console.log('Received version from Electron:', version);
          setLocalVersion(version || 'Unknown');
        } else {
          console.error('electronAPI.getAppVersion is not available');
          setLocalVersion('Unknown');
        }
      } catch (error) {
        console.error('Error getting app version:', error);
        setLocalVersion('Error');
      }
    };
    
    getAppVersion();
  }, []);

  // Sync activation key from props when it's updated (e.g., from App.jsx's initial fetch)
  useEffect(() => {
    setCurrentActivationKey(activationKey);
  }, [activationKey]);

  // Function to check monitoring status
  const checkMonitoringStatus = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/status`); // Route changed
      if (!response.ok) throw new Error('Failed to fetch monitoring status');
      const data = await response.json();
      setMonitoringStatus(data.running); // Property name changed
    } catch (error) {
      console.error('Error checking monitoring status:', error);
      setMessage('Failed to get monitoring status.');
      setMessageType('error');
    }
  };

  useEffect(() => {
    checkMonitoringStatus(); // Initial check
    const interval = setInterval(checkMonitoringStatus, 1000); // Poll every second
    return () => clearInterval(interval); // Cleanup
  }, [apiBaseUrl]);

  const handleSaveActivationKey = async () => {
    if (!currentActivationKey.trim()) {
      setMessage('Please enter an activation key.');
      setMessageType('warning');
      return;
    }

    setMessage(''); // Clear previous messages
    setIsSaving(true); // Start saving state

    try {
      const response = await fetch(`${apiBaseUrl}/activation`, { // Route changed
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activation_key: currentActivationKey }), // Key name changed
      });

      const data = await response.json();
      if (response.ok && data.success) { // Property name changed
        setMessage('Activation key saved successfully!');
        setMessageType('success');
        
        // Refresh the application after successful activation
        setTimeout(() => {
          if (window.electronAPI && window.electronAPI.reloadApp) {
            window.electronAPI.reloadApp();
          } else {
            // Fallback for web environment
            window.location.reload();
          }
        }, 1500); // Wait 1.5 seconds to show the success message
      } else {
        setMessage(data.message || 'Could not save activation key.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error saving activation key:', error);
      setMessage('Error connecting to server to save activation key.');
      setMessageType('error');
    } finally {
      setIsSaving(false); // End saving state
    }
  };

  const startMonitoring = async () => {
    setMessage('');
    try {
      const response = await fetch(`${apiBaseUrl}/start`, { method: 'POST' }); // Route changed
      const data = await response.json();
      if (response.ok && data.started) { // Property name changed
        setMessage('Monitoring started successfully.');
        setMessageType('success');
      } else {
        setMessage(data.message || 'Failed to start monitoring.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
      setMessage('Connection error: Could not connect to backend to start monitoring.');
      setMessageType('error');
    }
  };

  const stopMonitoring = async () => {
    setMessage('');
    try {
      const response = await fetch(`${apiBaseUrl}/stop`, { method: 'POST' }); // Route changed
      const data = await response.json();
      if (response.ok && data.stopped) { // Property name changed
        setMessage('Monitoring stopped successfully.');
        setMessageType('success');
      } else {
        setMessage(data.message || 'Failed to stop monitoring.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error stopping monitoring:', error);
      setMessage('Connection error: Could not connect to backend to stop monitoring.');
      setMessageType('error');
    }
  };

  const getRemoteVersion = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/version/remote`); // Route changed
      if (!response.ok) throw new Error('Failed to fetch remote version.');
      const data = await response.json();
      return data.remote_version; // Property name changed
    } catch (error) {
      console.error('Error fetching remote version:', error);
      setMessage('Could not fetch the latest version.');
      setMessageType('error');
      return null;
    }
  };

  const performFullUpdate = async (remoteVersion) => {
    setMessage('Starting update...');
    setMessageType('info');
    try {
      const response = await fetch(`${apiBaseUrl}/update`, { // Route changed
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ version: remoteVersion }),
      });

      const data = await response.json();
      if (response.ok && data.updated_files) { // Property name changed
        setMessage(data.message || `Updated to v${remoteVersion} successfully!`);
        setMessageType('success');
      } else {
        setMessage(data.message || 'Update failed.');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error performing update:', error);
      setMessage('Error connecting to backend for update.');
      setMessageType('error');
    }
  };

  const checkAndPromptUpdate = async () => {
    setIsCheckingUpdate(true);
    setMessage('');
    const remoteVersion = await getRemoteVersion();
    setIsCheckingUpdate(false);

    if (!remoteVersion) {
      return;
    }

    if (remoteVersion > localVersion) {
      const confirmUpdate = window.confirm(
        `A new version is available.\n\nLocal: v${localVersion}\nRemote: v${remoteVersion}\n\nDo you want to update now?`
      );
      if (confirmUpdate) {
        await performFullUpdate(remoteVersion);
      } else {
        setMessage('Update skipped. You can update later from the Welcome page.');
        setMessageType('info');
      }
    } else {
      const confirmRedownload = window.confirm(
        `You are already on the latest version (v${localVersion}).\n\nDo you want to re-download it anyway?`
      );
      if (confirmRedownload) {
        await performFullUpdate(remoteVersion);
      }
    }
  };

  const welcomeText = userInfo?.fullName ? `Welcome back, ${userInfo.fullName}` : "Welcome to CubiView";

  const getMessageClasses = () => {
    switch (messageType) {
      case 'success': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'error': return 'bg-red-50 text-red-700 border-red-200';
      case 'warning': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'info': return 'bg-blue-50 text-blue-700 border-blue-200';
      default: return '';
    }
  };

  const getMessageIcon = () => {
    switch (messageType) {
      case 'success': return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'info': return <Info className="w-5 h-5 text-blue-500" />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Compact Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mr-4">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                {welcomeText}
              </h1>
              <p className="text-gray-600 text-sm">Comprehensive employee monitoring and endpoint control</p>
            </div>
          </div>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-4 p-3 border rounded-lg shadow-sm ${getMessageClasses()}`}>
            <div className="flex items-center">
              <div className="mr-3">{getMessageIcon()}</div>
              <span className="font-medium text-sm">{message}</span>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* System Information */}
          <div className="bg-white/80 backdrop-blur-sm p-5 shadow-xl rounded-xl border border-white/20">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <Server className="w-5 h-5 text-blue-500 mr-2" />
              System Info
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">System ID:</span>
                <span className="text-gray-800 font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                  {systemId}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Version:</span>
                <span className="text-gray-800 font-semibold text-sm">v{localVersion}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Status:</span>
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${monitoringStatus ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                  <span className={`font-semibold text-sm ${monitoringStatus ? 'text-green-600' : 'text-gray-500'}`}>
                    {monitoringStatus ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Activation Key */}
          <div className="bg-white/80 backdrop-blur-sm p-5 shadow-xl rounded-xl border border-white/20">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <Key className="w-5 h-5 text-green-500 mr-2" />
              Activation Key
            </h3>
            <div className="space-y-3">
              <input
                type="text"
                id="activationKey"
                value={currentActivationKey}
                onChange={(e) => setCurrentActivationKey(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white text-sm"
                placeholder="Enter activation key..."
              />
              <button
                onClick={handleSaveActivationKey}
                disabled={isSaving}
                className={`w-full py-2 px-4 rounded-lg font-semibold shadow-md transition-all duration-200 text-sm ${
                  isSaving 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 hover:shadow-lg'
                } text-white`}
              >
                {isSaving ? (
                  <div className="flex items-center justify-center">
                    <RefreshCw className="animate-spin mr-2 h-4 w-4" />
                    Saving...
                  </div>
                ) : (
                  'Save Key'
                )}
              </button>
            </div>
          </div>

          {/* Control Panel */}
          <div className="bg-white/80 backdrop-blur-sm p-5 shadow-xl rounded-xl border border-white/20">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <Settings className="w-5 h-5 text-purple-500 mr-2" />
              Controls
            </h3>
            <div className="space-y-3">
              <button
                className={`
                  w-full py-2 px-4 rounded-lg font-semibold shadow-md transition-all duration-200 text-sm
                  ${monitoringStatus 
                    ? 'bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white' 
                    : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white'
                  }
                `}
                onClick={monitoringStatus ? stopMonitoring : startMonitoring}
              >
                <div className="flex items-center justify-center">
                  {monitoringStatus ? (
                    <>
                      <Square className="w-4 h-4 mr-2" />
                      Stop Monitoring
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Start Monitoring
                    </>
                  )}
                </div>
              </button>
              
              <button
                onClick={checkAndPromptUpdate}
                disabled={isCheckingUpdate}
                className="w-full py-2 px-4 bg-gradient-to-r from-cyan-500 to-teal-600 hover:from-cyan-600 hover:to-teal-700 text-white font-semibold rounded-lg shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                <div className="flex items-center justify-center">
                  {isCheckingUpdate ? (
                    <>
                      <RefreshCw className="animate-spin mr-2 h-4 w-4" />
                      Checking...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Check Updates
                    </>
                  )}
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Feature Overview - Compact */}
        <div className="bg-white/80 backdrop-blur-sm p-5 shadow-xl rounded-xl border border-white/20 mt-6">
          <div className="flex items-center mb-4">
            <Activity className="w-5 h-5 text-indigo-500 mr-2" />
            <h3 className="text-lg font-bold text-gray-800">Monitoring Features</h3>
          </div>
          <div className="grid md:grid-cols-4 gap-4 text-center">
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-blue-600 font-semibold text-sm mb-1">Activity Tracking</div>
              <div className="text-gray-600 text-xs">User behavior monitoring</div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-green-600 font-semibold text-sm mb-1">Application Usage</div>
              <div className="text-gray-600 text-xs">Real-time app monitoring</div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <div className="text-purple-600 font-semibold text-sm mb-1">Security Controls</div>
              <div className="text-gray-600 text-xs">USB & download restrictions</div>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="text-orange-600 font-semibold text-sm mb-1">Daily Reports</div>
              <div className="text-gray-600 text-xs">Comprehensive analytics</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;