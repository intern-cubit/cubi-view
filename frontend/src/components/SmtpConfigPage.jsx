import React, { useState, useEffect } from 'react';
import { Mail, Server, Info, Eye, EyeOff, Loader2, Save } from 'lucide-react';

const SmtpConfigPage = ({ apiBaseUrl }) => {
  const [config, setConfig] = useState({
    email: '',
    password: '', // This will not be loaded back from backend for security reasons
    recipient_email: '',
    cc1: '',
    cc2: '',
    smtp_server: '',
    smtp_port: '', // Initialize as string, convert to number when needed for comparisons
  });
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // Can be 'success', 'error', 'warning', 'info'
  const [isSavingAndSending, setIsSavingAndSending] = useState(false); // Combined state for saving and sending test email
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility

  const commonConfigs = [
    { name: 'Gmail', server: 'smtp.gmail.com', port: 465 },
    { name: 'Outlook/Hotmail', server: 'smtp-mail.outlook.com', port: 465 },
    { name: 'Yahoo', server: 'smtp.mail.yahoo.com', port: 465 },
    { name: 'Custom', server: '', port: '' } // Changed port to '' for custom, as it might not always be 587
  ];

  useEffect(() => {
    const loadSmtpConfig = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/smtp/config`);
        if (!response.ok) throw new Error('Failed to load SMTP config');
        const data = await response.json();
        // Ensure data fields are properly handled, especially for port which might be stored as string
        setConfig(prev => ({
          ...prev,
          email: data.from_email || '', // Backend sends 'from_email'
          recipient_email: data.to_email || '', // Backend sends 'to_email'
          cc1: data.cc1 || '',
          cc2: data.cc2 || '',
          smtp_server: data.smtp_server || '',
          smtp_port: data.smtp_port ? String(data.smtp_port) : '', // Convert to string for input value
        }));
      } catch (error) {
        console.error('Error loading SMTP config:', error);
        setMessage('Failed to load SMTP configuration. Please ensure backend route `/api/smtp/config` is implemented.');
        setMessageType('error');
      }
    };
    loadSmtpConfig();
  }, [apiBaseUrl]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    // For smtp_port, ensure it's stored as a string as input type="number" returns string
    setConfig(prev => ({ ...prev, [name]: name === 'smtp_port' ? String(value) : value }));
  };

  const handleQuickConfig = (selectedConfig) => {
    setConfig(prev => ({
      ...prev,
      smtp_server: selectedConfig.server,
      smtp_port: String(selectedConfig.port), // Ensure port is a string
    }));
  };

  const handleSaveAndSendTestEmail = async () => {
    const { email, password, recipient_email, smtp_server, smtp_port } = config;

    if (!email || !password || !recipient_email || !smtp_server || !smtp_port) {
      setMessage("Please fill in From Email, SMTP Server, SMTP Port, App Password, and Primary Recipient address.");
      setMessageType('warning');
      return;
    }

    setIsSavingAndSending(true);
    setMessage(''); // Clear previous messages

    try {
      // Step 1: Save configuration
      const saveResponse = await fetch(`${apiBaseUrl}/smtp/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: config.email,
            password: config.password,
            recipient_email: config.recipient_email,
            cc1: config.cc1,
            cc2: config.cc2,
            smtp_server: config.smtp_server,
            smtp_port: config.smtp_port,
        }),
      });

      const saveData = await saveResponse.json();

      if (saveResponse.ok && saveData.success) {
        setMessage('SMTP settings saved successfully!');
        setMessageType('success');

        // Step 2: Send test email
        const testEmailResponse = await fetch(`${apiBaseUrl}/smtp/send-test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // Send the complete config including password for the test email
          body: JSON.stringify({
            email: config.email,
            password: config.password,
            recipient_email: config.recipient_email,
            cc1: config.cc1,
            cc2: config.cc2,
            smtp_server: config.smtp_server,
            smtp_port: config.smtp_port,
          }),
        });
        const testEmailData = await testEmailResponse.json();

        if (testEmailResponse.ok && testEmailData.success) {
          setMessage(prev => prev + ' Test email sent successfully!');
          setMessageType('success');
        } else {
          setMessage(prev => prev + ' Failed to send test email: ' + (testEmailData.message || 'Unknown error.'));
          setMessageType('warning'); // Use warning for test email failure after save success
        }
      } else {
        setMessage('Failed to save SMTP settings: ' + (saveData.message || 'Unknown error.'));
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error saving or sending test email:', error);
      setMessage('Connection error: Could not save SMTP settings or send test email.');
      setMessageType('error');
    } finally {
      setIsSavingAndSending(false);
    }
  };

  const getMessageClasses = () => {
    switch (messageType) {
      case 'success': return 'bg-green-100 text-green-700 border-green-400';
      case 'error': return 'bg-red-100 text-red-700 border-red-400';
      case 'warning': return 'bg-yellow-100 text-yellow-700 border-yellow-400';
      case 'info': return 'bg-blue-100 text-blue-700 border-blue-400';
      default: return '';
    }
  };

  return (
    <div className="container mx-auto my-8 p-4">
      <h3 className="text-3xl font-semibold mb-6 text-gray-800">Simple Mail Transfer Protocol (SMTP) Configuration</h3>
      {message && (
        <div className={`mb-4 p-3 border rounded ${getMessageClasses()}`}>
          {message}
        </div>
      )}

      <div className="bg-white p-8 shadow-xl rounded-lg border border-gray-200">
        <form className="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-6">
          {/* Email Credentials Column */}
          <div className="lg:col-span-1 space-y-6">
            <div>
              <label htmlFor="email" className="block text-gray-700 text-sm font-bold mb-2">
                From Email Address *
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="e.g., yourname@example.com"
                  value={config.email}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                  required
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-gray-700 text-sm font-bold mb-2">
                App Password / Email Password *
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  placeholder="Use an App Password for Gmail/Outlook"
                  value={config.password}
                  onChange={handleChange}
                  className="w-full p-4 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(prev => !prev)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-xs text-amber-800 flex items-start">
                  <Info className="mr-2 mt-0.5 flex-shrink-0" size={14} />
                  <span>
                    <strong>Important:</strong> For Gmail/Outlook, use an{' '}
                    <a
                      href="https://support.google.com/accounts/answer/185833?hl=en"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-amber-600 hover:underline font-medium"
                    >
                      App Password
                    </a>{' '}
                    if 2-Factor Authentication is enabled.
                  </span>
                </p>
              </div>
            </div>

            <div>
              <label htmlFor="recipient_email" className="block text-gray-700 text-sm font-bold mb-2">
                Primary Recipient (To) *
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="recipient_email"
                  name="recipient_email"
                  placeholder="e.g., recipient@example.com"
                  value={config.recipient_email}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                  required
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>
          </div>

          {/* SMTP Server Configuration Column */}
          <div className="lg:col-span-1 space-y-6">
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-3">
                Quick SMTP Setup
              </label>
              <div className="grid grid-cols-2 gap-2">
                {commonConfigs.map((c) => (
                  <button
                    key={c.name}
                    type="button"
                    onClick={() => handleQuickConfig(c)}
                    className={`p-3 text-sm font-medium rounded-lg border transition-all duration-200 flex items-center justify-center
                      ${config.smtp_server === c.server && config.smtp_port === String(c.port) // Strict equality with string conversion
                        ? 'bg-blue-100 border-blue-500 text-blue-700 shadow-md'
                        : 'bg-gray-50 border-gray-300 text-gray-700 hover:bg-gray-100'
                      }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="smtp_server" className="block text-gray-700 text-sm font-bold mb-2">
                SMTP Server *
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="smtp_server"
                  name="smtp_server"
                  placeholder="e.g., smtp.gmail.com"
                  value={config.smtp_server}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                  required
                />
                <Server className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>

            <div>
              <label htmlFor="smtp_port" className="block text-gray-700 text-sm font-bold mb-2">
                SMTP Port *
              </label>
              <div className="relative">
                <input
                  type="number"
                  id="smtp_port"
                  name="smtp_port"
                  placeholder="e.g., 587 (TLS) or 465 (SSL)"
                  value={config.smtp_port}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                  required
                />
                <Server className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Common ports: 587 (TLS), 465 (SSL), 25 (unsecured)
              </div>
            </div>
          </div>

          {/* CC recipients side by side - this entire div now spans both columns */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <div>
              <label htmlFor="cc1" className="block text-gray-700 text-sm font-bold mb-2">
                CC Recipient 1 (Optional)
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="cc1"
                  name="cc1"
                  placeholder="e.g., cc1@example.com"
                  value={config.cc1}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>

            <div>
              <label htmlFor="cc2" className="block text-gray-700 text-sm font-bold mb-2">
                CC Recipient 2 (Optional)
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="cc2"
                  name="cc2"
                  placeholder="e.g., cc2@example.com"
                  value={config.cc2}
                  onChange={handleChange}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 text-gray-900 shadow-inner text-base transition-all duration-200 pl-10"
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              </div>
            </div>
          </div>

          {/* Save Button - spans both columns */}
          <div className="lg:col-span-2 mt-6">
            <button
              type="button"
              onClick={handleSaveAndSendTestEmail}
              disabled={isSavingAndSending || !config.email || !config.password || !config.recipient_email || !config.smtp_server || !config.smtp_port}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {isSavingAndSending ? (
                <>
                  <Loader2 className="mr-3 animate-spin" size={20} />
                  Saving & Testing...
                </>
              ) : (
                <>
                  <Save className="mr-3" size={20} />
                  Save and Send Test Email
                </>
              )}
            </button>
          </div>
        </form>

        <p className="mt-8 text-center text-gray-600 leading-relaxed text-sm">
          <strong className="text-lg text-gray-800">Please Note:</strong> Once the "From" and "To" email addresses are set,
          the employee's daily reports will be emailed automatically to the "To" address.
        </p>
      </div>
    </div>
  );
};

export default SmtpConfigPage;