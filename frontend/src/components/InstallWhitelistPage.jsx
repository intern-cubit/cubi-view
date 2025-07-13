import React, { useState, useEffect } from 'react';
import { 
  Download, 
  Shield, 
  ShieldCheck, 
  Plus, 
  Trash2, 
  Settings, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Info,
  Search,
  Package,
  HardDrive,
  FileText
} from 'lucide-react';

const InstallWhitelistPage = ({ apiBaseUrl = 'http://localhost:3000' }) => {
  const [processInput, setProcessInput] = useState('');
  const [whitelistedProcesses, setWhitelistedProcesses] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchWhitelistedProcesses = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/installers`);
      if (!response.ok) throw new Error('Failed to fetch whitelisted processes');
      const data = await response.json();
      setWhitelistedProcesses(data.installers || []);
    } catch (error) {
      console.error('Error fetching whitelisted processes:', error);
      setMessage('Failed to load whitelisted processes.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWhitelistedProcesses();
  }, [apiBaseUrl]);

  const handleAddProcess = async () => {
    const newProcess = processInput.trim().toLowerCase();
    if (!newProcess) {
      setMessage('Please enter a process name.');
      setMessageType('warning');
      return;
    }

    setMessage('');

    if (whitelistedProcesses.includes(newProcess)) {
      setMessage(`'${newProcess}' is already whitelisted.`);
      setMessageType('info');
      return;
    }

    // Optimistic update
    setWhitelistedProcesses(prev => [...prev, newProcess]);
    setProcessInput('');

    try {
      const response = await fetch(`${apiBaseUrl}/installers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newProcess }),
      });

      const data = await response.json();
      if (response.ok && data.installers) {
        setMessage(`'${newProcess}' has been added successfully.`);
        setMessageType('success');
        setWhitelistedProcesses(data.installers);
      } else {
        setMessage(data.message || `Failed to add '${newProcess}'.`);
        setMessageType('error');
        setWhitelistedProcesses(prev => prev.filter(p => p !== newProcess));
      }
    } catch (error) {
      console.error('Error adding process:', error);
      setMessage('Connection error: Failed to add process.');
      setMessageType('error');
      setWhitelistedProcesses(prev => prev.filter(p => p !== newProcess));
    }
  };

  const handleRemoveProcess = async (processToRemove) => {
    setMessage('');

    // Optimistic update
    setWhitelistedProcesses(prev => prev.filter(p => p !== processToRemove));

    try {
      const response = await fetch(`${apiBaseUrl}/installers`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: processToRemove }),
      });

      const data = await response.json();
      if (response.ok && data.installers) {
        setMessage(`'${processToRemove}' removed successfully.`);
        setMessageType('success');
        setWhitelistedProcesses(data.installers);
      } else {
        setMessage(data.message || `Failed to remove '${processToRemove}'.`);
        setMessageType('error');
        setWhitelistedProcesses(prev => [...prev, processToRemove].sort());
      }
    } catch (error) {
      console.error('Error removing process:', error);
      setMessage('Connection error: Failed to remove process.');
      setMessageType('error');
      setWhitelistedProcesses(prev => [...prev, processToRemove].sort());
    }
  };

  const getMessageIcon = () => {
    switch (messageType) {
      case 'success': return <CheckCircle className="w-5 h-5" />;
      case 'error': return <XCircle className="w-5 h-5" />;
      case 'warning': return <AlertCircle className="w-5 h-5" />;
      case 'info': return <Info className="w-5 h-5" />;
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

  const getProcessIcon = (processName) => {
    if (processName.includes('setup') || processName.includes('install')) {
      return <Download className="w-5 h-5 text-blue-600" />;
    } else if (processName.includes('uninstall')) {
      return <Trash2 className="w-5 h-5 text-red-600" />;
    } else if (processName.includes('.msi')) {
      return <Package className="w-5 h-5 text-green-600" />;
    } else {
      return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const filteredProcesses = whitelistedProcesses.filter(process => 
    process.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">Installer Access Control</h1>
          </div>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Manage whitelisted installer and uninstaller processes to control software installation permissions
          </p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border-2 flex items-center space-x-3 ${getMessageClasses()}`}>
            {getMessageIcon()}
            <span className="font-medium">{message}</span>
          </div>
        )}

        {/* Add Process Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
          <div className="flex items-center mb-6">
            <Settings className="w-8 h-8 text-blue-600 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Add New Process</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="processInput" className="block text-gray-700 text-lg font-semibold mb-3">
                Process Name:
              </label>
              <div className="relative">
                <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="processInput"
                  placeholder="e.g., setup.exe, installer.msi, uninstaller.exe"
                  value={processInput}
                  onChange={(e) => setProcessInput(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddProcess()}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Enter the exact process name including file extension (e.g., .exe, .msi)
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button
                className="flex-1 flex items-center justify-center px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                onClick={handleAddProcess}
                disabled={loading}
              >
                <Plus className="w-5 h-5 mr-2" />
                Add to Whitelist
              </button>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search processes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Whitelisted Processes */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6">
            <div className="flex items-center">
              <ShieldCheck className="w-8 h-8 text-white mr-3" />
              <div>
                <h3 className="text-2xl font-bold text-white">Whitelisted Processes</h3>
                <p className="text-blue-100">Allowed installer/uninstaller processes ({filteredProcesses.length})</p>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="max-h-96 overflow-y-auto">
              {filteredProcesses.length === 0 ? (
                <div className="text-center py-12">
                  <HardDrive className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">
                    {searchTerm ? 'No matching processes found' : 'No processes whitelisted yet'}
                  </p>
                  <p className="text-gray-400 text-sm mt-2">
                    Add installer or uninstaller processes to allow them to run
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredProcesses.map((process, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors group">
                      <div className="flex items-center">
                        {getProcessIcon(process)}
                        <span className="text-gray-800 font-medium ml-3">{process}</span>
                      </div>
                      <button
                        className="flex items-center px-3 py-2 text-sm bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors opacity-70 group-hover:opacity-100"
                        onClick={() => handleRemoveProcess(process)}
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Download className="w-8 h-8 text-blue-600 mr-3" />
              <h3 className="text-lg font-bold text-gray-800">Installers</h3>
            </div>
            <p className="text-gray-600">
              Processes that install new software on the system
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Examples: setup.exe, installer.msi, install.exe
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Trash2 className="w-8 h-8 text-red-600 mr-3" />
              <h3 className="text-lg font-bold text-gray-800">Uninstallers</h3>
            </div>
            <p className="text-gray-600">
              Processes that remove software from the system
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Examples: uninstall.exe, uninst.exe, remove.exe
            </p>
          </div>

          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Shield className="w-8 h-8 text-green-600 mr-3" />
              <h3 className="text-lg font-bold text-gray-800">Security</h3>
            </div>
            <p className="text-gray-600">
              Only whitelisted processes can perform installations
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Total processes: {whitelistedProcesses.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstallWhitelistPage;