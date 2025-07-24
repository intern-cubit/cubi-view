import React, { useState, useEffect } from 'react';
import { FileText, RefreshCw, ExternalLink, Calendar, User, AlertCircle, CheckCircle, AlertTriangle, Info, Mail, Send } from 'lucide-react';

const EmployeeReportPage = ({ apiBaseUrl }) => {
  const [reportHtml, setReportHtml] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('success');
  const [isLoading, setIsLoading] = useState(false);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [reportDate, setReportDate] = useState(null);
  const [hasReportData, setHasReportData] = useState(false);

  const fetchReport = async () => {
    setIsLoading(true);
    setMessage('');
    try {
      const metadataResponse = await fetch(`${apiBaseUrl}/reports/daily-html`);
      if (!metadataResponse.ok) {
        throw new Error('Failed to get report metadata.');
      }
      const metadata = await metadataResponse.json();

      if (metadata.status === 'success' && metadata.html_path && metadata.report_date) {
        setReportDate(metadata.report_date);
        setHasReportData(metadata.has_data);

        const previewResponse = await fetch(`${apiBaseUrl}/reports/preview`);
        if (!previewResponse.ok) {
          throw new Error('Failed to fetch report HTML preview.');
        }
        const html = await previewResponse.text();
        setReportHtml(html);

        if (metadata.has_data) {
          setMessage('Report loaded successfully.');
          setMessageType('success');
        } else {
          setMessage('Report generated, but no activity data was found for today. Please ensure monitoring is active.');
          setMessageType('warning');
        }
      } else {
        throw new Error(metadata.message || 'Report generation failed on backend.');
      }
    } catch (error) {
      console.error('Error fetching report:', error);
      setMessage(`Failed to load employee report: ${error.message || String(error)}. Ensure backend is running and reports are generated.`);
      setMessageType('error');
      setReportHtml('<p class="text-red-600 p-4">Could not load report. Please generate it first and ensure backend routes are active.</p>');
      setReportDate(null);
      setHasReportData(false);
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async () => {
    setIsLoading(true);
    setMessage('');
    try {
      const response = await fetch(`${apiBaseUrl}/reports/generate`, { method: 'POST' });
      console.log(response)
      const data = await response.json();
      console.log('Report generation response:', data);

      if (response.ok && data.status === 'success') {
        setReportDate(data.report_date);
        setHasReportData(data.has_data);

        if (data.has_data) {
          setMessage(data.message || 'Report generation initiated. Please wait a moment and refresh.');
          setMessageType('success');
        } else {
          setMessage('Report generated, but no activity data was found for today. Please ensure monitoring is active.');
          setMessageType('warning');
        }
        setTimeout(fetchReport, 1500);
      } else {
        throw new Error(data.message || 'Failed to generate report');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      setMessage(`Failed to generate report: ${error.message || String(error)}`);
      setMessageType('error');
      setHasReportData(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [apiBaseUrl]);

  const openFullReportInBrowser = () => {
    if (reportDate) {
      const reportUrl = `${apiBaseUrl}/reports/view_dated/${reportDate}/CubiView_Summary_Report.html`;
      window.open(reportUrl, '_blank');
    } else {
      setMessage('Please generate a report first to open it in a new browser tab.');
      setMessageType('warning');
    }
  };

  const sendReportToSmtpEmails = async () => {
    setIsSendingEmail(true);
    setMessage('');
    try {
      const response = await fetch(`${apiBaseUrl}/reports/send-to-smtp-emails`, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      console.log('Email send response:', data);

      if (response.ok && data.success) {
        setMessage(`Report sent successfully to ${data.recipients?.to}${data.recipients?.cc?.length > 0 ? ` and CC: ${data.recipients.cc.join(', ')}` : ''}`);
        setMessageType('success');
      } else {
        throw new Error(data.message || 'Failed to send report via email');
      }
    } catch (error) {
      console.error('Error sending report via email:', error);
      setMessage(`Failed to send report via email: ${error.message || String(error)}`);
      setMessageType('error');
    } finally {
      setIsSendingEmail(false);
    }
  };

  const getMessageIcon = () => {
    switch (messageType) {
      case 'success': return <CheckCircle className="h-5 w-5" />;
      case 'error': return <AlertCircle className="h-5 w-5" />;
      case 'warning': return <AlertTriangle className="h-5 w-5" />;
      case 'info': return <Info className="h-5 w-5" />;
      default: return <Info className="h-5 w-5" />;
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <User className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-800">Employee Report Dashboard</h1>
          </div>
          <p className="text-gray-600 text-lg">Daily Work Report for Employee No.1</p>
          {reportDate && (
            <div className="inline-flex items-center gap-2 mt-2 px-4 py-2 bg-white rounded-full shadow-sm border">
              <Calendar className="h-4 w-4 text-blue-600" />
              <span className="text-sm text-gray-700">Report Date: {reportDate}</span>
            </div>
          )}
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 border rounded-xl shadow-sm ${getMessageClasses()}`}>
            <div className="flex items-center gap-3">
              {getMessageIcon()}
              <span className="font-medium">{message}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8 justify-center">
          <button
            className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            onClick={generateReport}
            disabled={isLoading || isSendingEmail}
          >
            <div className="flex items-center justify-center gap-3">
              {isLoading ? (
                <RefreshCw className="h-5 w-5 animate-spin" />
              ) : (
                <FileText className="h-5 w-5" />
              )}
              <span>{isLoading ? 'Generating Report...' : 'Generate New Report'}</span>
            </div>
          </button>
          
          <button
            className="group px-8 py-4 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 border border-gray-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            onClick={openFullReportInBrowser}
            disabled={!reportDate || isLoading || isSendingEmail}
          >
            <div className="flex items-center justify-center gap-3">
              <ExternalLink className="h-5 w-5 text-blue-600" />
              <span>Open Full Report</span>
            </div>
          </button>

          <button
            className="group px-8 py-4 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            onClick={sendReportToSmtpEmails}
            disabled={!reportDate || isLoading || isSendingEmail}
          >
            <div className="flex items-center justify-center gap-3">
              {isSendingEmail ? (
                <RefreshCw className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
              <span>{isSendingEmail ? 'Sending Email...' : 'Send to SMTP Emails'}</span>
            </div>
          </button>
        </div>

        {/* Report Preview Card */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <FileText className="h-5 w-5 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-gray-800">Report Preview</h2>
            </div>
          </div>
          
          <div className="p-6">
            <div
              className="min-h-[500px] border border-gray-200 rounded-xl p-6 bg-gray-50/50 overflow-y-auto"
              dangerouslySetInnerHTML={{ __html: reportHtml }}
            />
          </div>
        </div>

        {/* Status Indicators */}
        <div className="mt-8 flex justify-center">
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${hasReportData ? 'bg-green-500' : 'bg-gray-300'}`}></div>
              <span>Data Available</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${reportDate ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
              <span>Report Generated</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-gray-300'}`}></div>
              <span>Processing</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isSendingEmail ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
              <span>Sending Email</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployeeReportPage;