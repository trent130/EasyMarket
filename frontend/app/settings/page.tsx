"use client";

import React, { useState } from "react";
import {
  Store,
  Bell,
  CreditCard,
  Truck,
  Mail,
  Shield,
  Globe,
  Palette,
  Save,
  /* Toggle, */
  DollarSign,
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";

interface SettingsState {
  storeName: string;
  email: string;
  currency: string;
  language: string;
  timezone: string;
  orderPrefix: string;
  enableNotifications: boolean;
  emailNotifications: boolean;
  darkMode: boolean;
  maintenanceMode: boolean;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsState>({
    storeName: "My Store",
    email: "store@example.com",
    currency: "USD",
    language: "en",
    timezone: "UTC",
    orderPrefix: "ORD",
    enableNotifications: true,
    emailNotifications: true,
    darkMode: false,
    maintenanceMode: false,
  });

  const [activeTab, setActiveTab] = useState("general");
  const [saved, setSaved] = useState(false);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    setSettings((prev) => ({
      ...prev,
      [name]:
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Settings saved:", settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const tabs = [
    { id: "general", label: "General", icon: Store },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "payments", label: "Payments", icon: CreditCard },
    { id: "shipping", label: "Shipping", icon: Truck },
    { id: "emails", label: "Emails", icon: Mail },
    { id: "security", label: "Security", icon: Shield },
  ];

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 grid grid-cols-12 overflow-y-visible mx-auto overscroll-y-contain">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-3xl font-bold text-gray-900">
                Store Settings
              </h1>
              <button
                onClick={handleSubmit}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </button>
            </div>

            {saved && (
              <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
                Settings saved successfully!
              </div>
            )}

            <div className="bg-white shadow rounded-lg">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                      group inline-flex items-center px-6 py-4 border-b-2 font-medium text-sm
                      ${
                        activeTab === tab.id
                          ? "border-indigo-500 text-indigo-600"
                          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                      }
                    `}
                    >
                      <tab.icon
                        className={`
                      h-5 w-5 mr-2
                      ${
                        activeTab === tab.id
                          ? "text-indigo-500"
                          : "text-gray-400 group-hover:text-gray-500"
                      }
                    `}
                      />
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>

              <div className="p-6">
                {activeTab === "general" && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Store Name
                      </label>
                      <input
                        aria-label="storename"
                        type="text"
                        name="storeName"
                        value={settings.storeName}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Store Email
                      </label>
                      <input
                        aria-label="email"
                        type="email"
                        name="email"
                        value={settings.email}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      />
                    </div>

                    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Currency
                        </label>
                        <select
                          aria-label="currency"
                          name="currency"
                          value={settings.currency}
                          onChange={handleInputChange}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        >
                          <option value="USD">USD ($)</option>
                          <option value="EUR">EUR (€)</option>
                          <option value="GBP">GBP (£)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Language
                        </label>
                        <select
                          aria-label="language"
                          name="language"
                          value={settings.language}
                          onChange={handleInputChange}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        >
                          <option value="en">English</option>
                          <option value="es">Spanish</option>
                          <option value="fr">French</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Timezone
                        </label>
                        <select
                          aria-label="timezone"
                          name="timezone"
                          value={settings.timezone}
                          onChange={handleInputChange}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        >
                          <option value="UTC">UTC</option>
                          <option value="EST">EST</option>
                          <option value="PST">PST</option>
                        </select>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-sm font-medium text-gray-700">
                            Dark Mode
                          </h3>
                          <p className="text-sm text-gray-500">
                            Enable dark mode for the admin interface
                          </p>
                        </div>
                        <button
                          aria-label="darkmode"
                          type="button"
                          onClick={() =>
                            setSettings((prev) => ({
                              ...prev,
                              darkMode: !prev.darkMode,
                            }))
                          }
                          className={`
                          relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer 
                          transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                          ${settings.darkMode ? "bg-indigo-600" : "bg-gray-200"}
                        `}
                        >
                          <span
                            className={`
                          pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition 
                          ease-in-out duration-200 ${
                            settings.darkMode
                              ? "translate-x-5"
                              : "translate-x-0"
                          }
                        `}
                          />
                        </button>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-sm font-medium text-gray-700">
                            Maintenance Mode
                          </h3>
                          <p className="text-sm text-gray-500">
                            Put your store in maintenance mode
                          </p>
                        </div>
                        <button
                          aria-label="maintmode"
                          type="button"
                          onClick={() =>
                            setSettings((prev) => ({
                              ...prev,
                              maintenanceMode: !prev.maintenanceMode,
                            }))
                          }
                          className={`
                          relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer 
                          transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                          ${
                            settings.maintenanceMode
                              ? "bg-indigo-600"
                              : "bg-gray-200"
                          }
                        `}
                        >
                          <span
                            className={`
                          pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition 
                          ease-in-out duration-200 ${
                            settings.maintenanceMode
                              ? "translate-x-5"
                              : "translate-x-0"
                          }
                        `}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === "notifications" && (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-700">
                          Push Notifications
                        </h3>
                        <p className="text-sm text-gray-500">
                          Receive push notifications for new orders
                        </p>
                      </div>
                      <button
                        aria-label="pushnotifications"
                        type="button"
                        onClick={() =>
                          setSettings((prev) => ({
                            ...prev,
                            enableNotifications: !prev.enableNotifications,
                          }))
                        }
                        className={`
                        relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer 
                        transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                        ${
                          settings.enableNotifications
                            ? "bg-indigo-600"
                            : "bg-gray-200"
                        }
                      `}
                      >
                        <span
                          className={`
                        pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition 
                        ease-in-out duration-200 ${
                          settings.enableNotifications
                            ? "translate-x-5"
                            : "translate-x-0"
                        }
                      `}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-700">
                          Email Notifications
                        </h3>
                        <p className="text-sm text-gray-500">
                          Receive email notifications for new orders
                        </p>
                      </div>
                      <button
                        aria-label="setSettings"
                        type="button"
                        onClick={() =>
                          setSettings((prev) => ({
                            ...prev,
                            emailNotifications: !prev.emailNotifications,
                          }))
                        }
                        className={`
                        relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer 
                        transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
                        ${
                          settings.emailNotifications
                            ? "bg-indigo-600"
                            : "bg-gray-200"
                        }
                      `}
                      >
                        <span
                          className={`
                        pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition 
                        ease-in-out duration-200 ${
                          settings.emailNotifications
                            ? "translate-x-5"
                            : "translate-x-0"
                        }
                      `}
                        />
                      </button>
                    </div>
                  </div>
                )}

                {/* Placeholder content for other tabs */}
                {activeTab === "payments" && (
                  <div className="text-gray-500">
                    Payment settings configuration options will appear here.
                  </div>
                )}
                {activeTab === "shipping" && (
                  <div className="text-gray-500">
                    Shipping settings configuration options will appear here.
                  </div>
                )}
                {activeTab === "emails" && (
                  <div className="text-gray-500">
                    Email template settings will appear here.
                  </div>
                )}
                {activeTab === "security" && (
                  <div className="text-gray-500">
                    Security and authentication settings will appear here.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
