import React from 'react';
import {
  Home,
  MapPin,
  Lock,
  Globe,
  Download,
  BarChart3,
  Mail,
  Info,
  Shield,
  Server,
  AlertCircle
} from 'lucide-react';

const Sidebar = ({ currentPage, onPageChange, isActivationKeyMissing }) => {
  const sidebarButtons = [
    {
      name: "welcome",
      text: "Welcome",
      icon: <Home className="w-5 h-5" />
    },
    {
      name: "track",
      text: "Monitoring Features",
      icon: <MapPin className="w-5 h-5" />
    },
    {
      name: "limit",
      text: "Limit Device Features",
      icon: <Lock className="w-5 h-5" />
    },
    {
      name: "website",
      text: "Whitelist / Blacklist Websites",
      icon: <Globe className="w-5 h-5" />
    },
    {
      name: "install_whitelist",
      text: "Whitelist Installs/Uninstalls",
      icon: <Download className="w-5 h-5" />
    },
    {
      name: "report",
      text: "View Report",
      icon: <BarChart3 className="w-5 h-5" />
    },
    {
      name: "smtp",
      text: "SMTP Configuration",
      icon: <Mail className="w-5 h-5" />
    },
    {
      name: "about",
      text: "About Us",
      icon: <Info className="w-5 h-5" />
    },
    {
      name: "privacy",
      text: "terms of Use",
      icon: <Shield className="w-5 h-5" />
    },
  ];

  const isItemDisabled = (itemName) => {
    return isActivationKeyMissing && itemName !== 'welcome';
  };

  return (
    <div className="w-72 flex-shrink-0 bg-gradient-to-b from-slate-50 to-slate-100 border-r border-slate-200 shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-slate-200 bg-white/50 backdrop-blur-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <Server className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">CubiView</h2>
            <p className="text-xs text-slate-500">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {sidebarButtons.map((button, index) => {
          const isActive = currentPage === button.name;
          const isDisabled = isItemDisabled(button.name);

          return (
            <div key={button.name} className="relative">
              <button
                className={`
                  w-full group flex items-center space-x-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ease-in-out transform hover:scale-[1.02] active:scale-[0.98]
                  ${isActive
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25'
                    : isDisabled
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-white text-slate-700 hover:bg-slate-50 hover:text-blue-600 border border-slate-200 hover:border-blue-200 shadow-sm hover:shadow-md'
                  }
                `}
                onClick={() => !isDisabled && onPageChange(button.name)}
                disabled={isDisabled}
              >
                {/* Icon */}
                <div className={`
                  flex-shrink-0 transition-all duration-200
                  ${isActive
                    ? 'text-white'
                    : isDisabled
                      ? 'text-slate-400'
                      : 'text-slate-500 group-hover:text-blue-500'
                  }
                `}>
                  {button.icon}
                </div>

                {/* Text */}
                <span className={`
                  text-sm leading-5 transition-all duration-200
                  ${isActive
                    ? 'text-white font-semibold'
                    : isDisabled
                      ? 'text-slate-400'
                      : 'text-slate-700 group-hover:text-slate-900'
                  }
                `}>
                  {button.text}
                </span>

                {/* Active indicator */}
                {isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full opacity-80"></div>
                )}

                {/* Disabled indicator */}
                {isDisabled && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Lock className="w-4 h-4 text-slate-400" />
                  </div>
                )}
              </button>

              {/* Hover effect for non-disabled items */}
              {!isDisabled && !isActive && (
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/0 to-indigo-600/0 group-hover:from-blue-500/5 group-hover:to-indigo-600/5 transition-all duration-200 pointer-events-none"></div>
              )}
            </div>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;