import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';

const VpnAdminDialog = ({ apiBaseUrl, isOpen, onClose }) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [adminCredentials, setAdminCredentials] = useState({ username: '', password: '' });
  const [showAuthForm, setShowAuthForm] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchVpnRequests();
      const interval = setInterval(fetchVpnRequests, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const fetchVpnRequests = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/vpn/admin-requests`);
      const data = await response.json();
      if (data.success) {
        setRequests(data.requests);
      }
    } catch (error) {
      console.error('Error fetching VPN requests:', error);
    }
  };

  const handleAdminAuth = async (action, requestId) => {
    setLoading(true);
    try {
      // First authenticate admin
      console.log('Authenticating admin...');
      console.log(adminCredentials)
      const authResponse = await fetch(`${apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: adminCredentials.username,
          password: adminCredentials.password
        })
      });

      const authData = await authResponse.json();
      console.log('Admin authentication response:', authData);
      if (!authResponse.ok || !authData.token) {
        throw new Error('Invalid admin credentials');
      }

      // Then perform the action
      const actionEndpoint = action === 'approve' ? '/vpn/admin-approve' : '/vpn/admin-deny';
      const actionResponse = await fetch(`${apiBaseUrl}${actionEndpoint}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authData.token}`
        },
        body: JSON.stringify({ request_id: requestId })
      });

      const actionData = await actionResponse.json();
      if (actionData.success) {
        alert(`VPN access ${action}d successfully`);
        setShowAuthForm(false);
        setSelectedRequest(null);
        setAdminCredentials({ username: '', password: '' });
        fetchVpnRequests();
      } else {
        throw new Error(actionData.message);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const showAuthDialog = (action, request) => {
    setSelectedRequest({ ...request, action });
    setShowAuthForm(true);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-500 to-red-600 px-6 py-4 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Shield className="w-6 h-6" />
              <h2 className="text-xl font-bold">VPN Access Requests</h2>
            </div>
            <button 
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {requests.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Shield className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">No pending VPN access requests</p>
            </div>
          ) : (
            <div className="space-y-4">
              {requests.map((request, index) => (
                <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="w-6 h-6 text-yellow-600 mt-1" />
                      <div>
                        <h3 className="font-semibold text-gray-800">VPN Detected</h3>
                        <p className="text-gray-600 text-sm">{request.message}</p>
                        <div className="flex items-center space-x-2 mt-2 text-sm text-gray-500">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(request.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => showAuthDialog('approve', request)}
                        className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm flex items-center space-x-1"
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span>Approve</span>
                      </button>
                      <button
                        onClick={() => showAuthDialog('deny', request)}
                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm flex items-center space-x-1"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Deny</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Admin Authentication Modal */}
      {showAuthForm && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 text-white rounded-t-lg">
              <h3 className="text-lg font-bold">Admin Authentication Required</h3>
              <p className="text-sm opacity-90">
                {selectedRequest?.action === 'approve' ? 'Approve' : 'Deny'} VPN access request
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Admin Username
                  </label>
                  <input
                    type="text"
                    value={adminCredentials.username}
                    onChange={(e) => setAdminCredentials(prev => ({ ...prev, username: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter admin username"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Admin Password
                  </label>
                  <input
                    type="password"
                    value={adminCredentials.password}
                    onChange={(e) => setAdminCredentials(prev => ({ ...prev, password: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter admin password"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowAuthForm(false);
                    setSelectedRequest(null);
                    setAdminCredentials({ username: '', password: '' });
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleAdminAuth(selectedRequest.action, selectedRequest.id)}
                  disabled={loading || !adminCredentials.username || !adminCredentials.password}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Authenticating...' : 'Authenticate'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VpnAdminDialog;
