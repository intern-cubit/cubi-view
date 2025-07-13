import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldCheck, 
  ShieldX, 
  Plus, 
  Trash2, 
  Globe, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Info,
  Search,
  Filter
} from 'lucide-react';

const WebsiteWhitelistPage = ({ apiBaseUrl = 'http://localhost:3000' }) => {
  const [websiteInput, setWebsiteInput] = useState('');
  const [whitelist, setWhitelist] = useState([]);
  const [blocklist, setBlocklist] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLists = async () => {
    setLoading(true);
    try {
      const whitelistRes = await fetch(`${apiBaseUrl}/whitelist`);
      const blocklistRes = await fetch(`${apiBaseUrl}/blocklist`);

      if (!whitelistRes.ok) throw new Error('Failed to fetch whitelist');
      if (!blocklistRes.ok) throw new Error('Failed to fetch blocklist');

      const whitelistData = await whitelistRes.json();
      const blocklistData = await blocklistRes.json();

      setWhitelist(whitelistData.whitelist || []);
      setBlocklist(blocklistData.blocklist || []);
    } catch (error) {
      console.error('Error fetching website lists:', error);
      setMessage('Failed to load website lists.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLists();
  }, [apiBaseUrl]);

  const validateUrl = (site) => {
    if (!site.trim()) {
      return { isValid: false, error: "Please enter a website." };
    }
    return { isValid: true, error: "" };
  };

  const handleAddToList = async (listType) => {
    const site = websiteInput.trim().toLowerCase();
    const { isValid, error } = validateUrl(site);

    if (!isValid) {
      setMessage(error);
      setMessageType('warning');
      return;
    }

    setMessage('');

    let currentList = listType === 'whitelist' ? whitelist : blocklist;
    const setList = listType === 'whitelist' ? setWhitelist : setBlocklist;

    if (currentList.includes(site)) {
      setMessage(`${site} is already in the ${listType}.`);
      setMessageType('info');
      return;
    }

    // Optimistic update
    setList(prev => [...prev, site]);
    setWebsiteInput('');

    try {
      const response = await fetch(`${apiBaseUrl}/${listType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site }),
      });

      const data = await response.json();
      if (response.ok && data[listType]) {
        setMessage(`'${site}' added to ${listType} successfully.`);
        setMessageType('success');
        setList(data[listType]);
      } else {
        setMessage(data.message || `Failed to add '${site}' to ${listType}.`);
        setMessageType('error');
        setList(prev => prev.filter(s => s !== site));
      }
    } catch (error) {
      console.error(`Error adding to ${listType}:`, error);
      setMessage(`Connection error: Failed to add '${site}' to ${listType}.`);
      setMessageType('error');
      setList(prev => prev.filter(s => s !== site));
    }
  };

  const handleRemoveFromList = async (listType, siteToRemove) => {
    setMessage('');

    const setList = listType === 'whitelist' ? setWhitelist : setBlocklist;
    setList(prev => prev.filter(site => site !== siteToRemove));

    try {
      const response = await fetch(`${apiBaseUrl}/${listType}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ site: siteToRemove }),
      });

      const data = await response.json();
      if (response.ok && data[listType]) {
        setMessage(`'${siteToRemove}' removed from ${listType} successfully.`);
        setMessageType('success');
        setList(data[listType]);
      } else {
        setMessage(data.message || `Failed to remove '${siteToRemove}' from ${listType}.`);
        setMessageType('error');
        setList(prev => [...prev, siteToRemove].sort());
      }
    } catch (error) {
      console.error(`Error removing from ${listType}:`, error);
      setMessage(`Connection error: Failed to remove '${siteToRemove}' from ${listType}.`);
      setMessageType('error');
      setList(prev => [...prev, siteToRemove].sort());
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

  const filteredWhitelist = whitelist.filter(site => 
    site.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredBlocklist = blocklist.filter(site => 
    site.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-12 h-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-800">Website Access Control</h1>
          </div>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Manage your website whitelist and blocklist to control access and enhance security
          </p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border-2 flex items-center space-x-3 ${getMessageClasses()}`}>
            {getMessageIcon()}
            <span className="font-medium">{message}</span>
          </div>
        )}

        {/* Add Website Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 mb-8">
          <div className="flex items-center mb-6">
            <Globe className="w-8 h-8 text-blue-600 mr-3" />
            <h2 className="text-2xl font-bold text-gray-800">Add New Website</h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="websiteInput" className="block text-gray-700 text-lg font-semibold mb-3">
                Website URL:
              </label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="websiteInput"
                  placeholder="e.g., google.com, https://chat.openai.com"
                  value={websiteInput}
                  onChange={(e) => setWebsiteInput(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button
                className="flex-1 flex items-center justify-center px-6 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                onClick={() => handleAddToList('whitelist')}
                disabled={loading}
              >
                <ShieldCheck className="w-5 h-5 mr-2" />
                Add to Whitelist
              </button>
              <button
                className="flex-1 flex items-center justify-center px-6 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                onClick={() => handleAddToList('blocklist')}
                disabled={loading}
              >
                <ShieldX className="w-5 h-5 mr-2" />
                Add to Blocklist
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
              placeholder="Search websites..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Lists Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Whitelist */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 p-6">
              <div className="flex items-center">
                <ShieldCheck className="w-8 h-8 text-white mr-3" />
                <div>
                  <h3 className="text-2xl font-bold text-white">Whitelisted Websites</h3>
                  <p className="text-emerald-100">Allowed websites ({filteredWhitelist.length})</p>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="max-h-96 overflow-y-auto">
                {filteredWhitelist.length === 0 ? (
                  <div className="text-center py-12">
                    <ShieldCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">
                      {searchTerm ? 'No matching websites found' : 'No websites whitelisted yet'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {filteredWhitelist.map((site, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <Globe className="w-5 h-5 text-emerald-600 mr-3" />
                          <span className="text-gray-800 font-medium">{site}</span>
                        </div>
                        <button
                          className="flex items-center px-3 py-2 text-sm bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                          onClick={() => handleRemoveFromList('whitelist', site)}
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

          {/* Blocklist */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-red-500 to-red-600 p-6">
              <div className="flex items-center">
                <ShieldX className="w-8 h-8 text-white mr-3" />
                <div>
                  <h3 className="text-2xl font-bold text-white">Blocked Websites</h3>
                  <p className="text-red-100">Blocked websites ({filteredBlocklist.length})</p>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="max-h-96 overflow-y-auto">
                {filteredBlocklist.length === 0 ? (
                  <div className="text-center py-12">
                    <ShieldX className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">
                      {searchTerm ? 'No matching websites found' : 'No websites blocked yet'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {filteredBlocklist.map((site, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                        <div className="flex items-center">
                          <Globe className="w-5 h-5 text-red-600 mr-3" />
                          <span className="text-gray-800 font-medium">{site}</span>
                        </div>
                        <button
                          className="flex items-center px-3 py-2 text-sm bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                          onClick={() => handleRemoveFromList('blocklist', site)}
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
        </div>

        {/* Stats Footer */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="flex items-center justify-center space-x-3">
              <ShieldCheck className="w-8 h-8 text-emerald-600" />
              <div>
                <p className="text-2xl font-bold text-gray-800">{whitelist.length}</p>
                <p className="text-gray-600">Whitelisted Sites</p>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-3">
              <ShieldX className="w-8 h-8 text-red-600" />
              <div>
                <p className="text-2xl font-bold text-gray-800">{blocklist.length}</p>
                <p className="text-gray-600">Blocked Sites</p>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold text-gray-800">{whitelist.length + blocklist.length}</p>
                <p className="text-gray-600">Total Managed</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebsiteWhitelistPage;