import React from 'react';

const PrivacyPolicyPage = () => {
  return (
    <div className="container mx-auto my-8">
      <h3 className="text-3xl font-semibold mb-6 text-gray-800">Privacy Policy</h3>
      <div className="bg-white p-8 shadow-xl rounded-lg text-gray-700 leading-relaxed">
        <p className="mb-4">
          Welcome to Cubi-View's Privacy Policy. Your privacy is critically important to us.
          This policy outlines how Cubi-View collects, uses, maintains, and discloses information collected from users (each, a "User") of the Cubi-View employee monitoring software.
        </p>
        <h5 className="text-xl font-semibold mt-6 mb-3">1. Information We Collect</h5>
        <ul className="list-disc list-inside space-y-2 mb-4">
          <li><strong>Monitoring Data:</strong> Cubi-View is designed to monitor employee activity on company-owned devices. This may include, but is not limited to: keystrokes, mouse clicks and movements, application usage, browser history, clipboard content, print job logs, login/logout times, screen lock/unlock events, periodic screenshots, audio clips, and video clips. Location data (IP/GPS-based) may also be collected.</li>
          <li><strong>Configuration Data:</strong> Settings configured by the administrator (e.g., feature toggles, website whitelists/blocklists, installation whitelists, SMTP configurations).</li>
          <li><strong>User Account Information:</strong> For admin login, we collect username and hashed password.</li>
        </ul>

        <h5 className="text-xl font-semibold mt-6 mb-3">2. How We Use Collected Information</h5>
        <ul className="list-disc list-inside space-y-2 mb-4">
          <li><strong>Employee Monitoring:</strong> All collected monitoring data is used solely for the purpose of employee productivity analysis, security, and compliance as agreed upon between Cubi-View's client (the employer) and their employees.</li>
          <li><strong>Software Functionality:</strong> Configuration data is used to enable and customize the software's features.</li>
          <li><strong>Communication:</strong> SMTP configuration is used to send automated daily reports to the designated recipients.</li>
          <li><strong>Improvements:</strong> We may use aggregated, anonymized data for software improvement and development.</li>
        </ul>

        <h5 className="text-xl font-semibold mt-6 mb-3">3. Data Storage and Security</h5>
        <ul className="list-disc list-inside space-y-2 mb-4">
          <li><strong>Local Storage:</strong> Most monitoring data is initially collected and stored locally on the monitored device before being sent to a designated secure server (as configured by the employer).</li>
          <li><strong>Encryption:</strong> Data transmission between the monitored device and the server, and between the GUI and the server, is encrypted using industry-standard protocols (e.g., HTTPS).</li>
          <li><strong>Access Control:</strong> Access to collected data is restricted to authorized personnel.</li>
          <li><strong>No Personal Data Sale:</strong> We do not sell, trade, or rent Users' personal identification information to others.</li>
        </ul>

        <h5 className="text-xl font-semibold mt-6 mb-3">4. Data Retention</h5>
        <p className="mb-4">
          Data retention periods are configurable by the client (employer) or based on their agreement with Cubi-View.
          Once data is no longer needed, it is securely deleted.
        </p>

        <h5 className="text-xl font-semibold mt-6 mb-3">5. Your Rights and Responsibilities</h5>
        <ul className="list-disc list-inside space-y-2 mb-4">
          <li><strong>Employer's Responsibility:</strong> The employer is responsible for informing their employees about the monitoring activities and ensuring compliance with all applicable local, national, and international privacy laws and regulations (e.g., GDPR, CCPA).</li>
          <li><strong>Data Access:</strong> Employees should consult their employer regarding their rights to access or rectify their monitored data.</li>
        </ul>

        <h5 className="text-xl font-semibold mt-6 mb-3">6. Changes to this Privacy Policy</h5>
        <p className="mb-4">
          Cubi-View has the discretion to update this privacy policy at any time. When we do, we will revise the updated date at the bottom of this page. We encourage Users to frequently check this page for any changes to stay informed about how we are helping to protect the personal information we collect. You acknowledge and agree that it is your responsibility to review this privacy policy periodically and become aware of modifications.
        </p>

        <h5 className="text-xl font-semibold mt-6 mb-3">7. Your Acceptance of These Terms</h5>
        <p className="mb-4">
          By using this Software, you signify your acceptance of this policy. If you do not agree to this policy, please do not use our Software. Your continued use of the Software following the posting of changes to this policy will be deemed your acceptance of those changes.
        </p>

        <p className="mt-8 text-sm text-gray-500"><em>Last updated: July 8, 2025</em></p>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;