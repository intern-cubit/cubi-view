import React from 'react';
import { X, AlertTriangle } from 'lucide-react';

const ConfirmationDialog = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = "Continue", 
  cancelText = "Cancel",
  type = "warning" // warning, danger, info
}) => {
  if (!isOpen) return null;

  const getTypeStyles = () => {
    switch (type) {
      case 'danger':
        return {
          headerBg: 'bg-gradient-to-r from-red-500 to-red-600',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          confirmBtn: 'bg-red-500 hover:bg-red-600'
        };
      case 'warning':
        return {
          headerBg: 'bg-gradient-to-r from-orange-500 to-orange-600',
          icon: <AlertTriangle className="w-6 h-6 text-orange-600" />,
          confirmBtn: 'bg-orange-500 hover:bg-orange-600'
        };
      default:
        return {
          headerBg: 'bg-gradient-to-r from-blue-500 to-blue-600',
          icon: <AlertTriangle className="w-6 h-6 text-blue-600" />,
          confirmBtn: 'bg-blue-500 hover:bg-blue-600'
        };
    }
  };

  const typeStyles = getTypeStyles();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        {/* Header with CubiView Logo */}
        <div className={`${typeStyles.headerBg} px-6 py-4 text-white`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {/* CubiView Logo */}
              <img 
                src="/CubiView.ico" 
                alt="CubiView" 
                className="w-8 h-8"
                onError={(e) => {
                  // Fallback to PNG if ICO fails
                  if (e.target.src.includes('.ico')) {
                    e.target.src = "/Cubiview-Cubicle.png";
                    e.target.className = "w-8 h-8 rounded";
                  }
                }}
              />
              <h2 className="text-lg font-bold">CubiView</h2>
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
        <div className="p-6">
          <div className="flex items-start space-x-4">
            {typeStyles.icon}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                {title}
              </h3>
              <p className="text-gray-600 mb-6">
                {message}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              className={`px-4 py-2 text-white rounded-md transition-colors ${typeStyles.confirmBtn}`}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;
