import React from 'react';
import { BarChart3, DollarSign, ShoppingCart, Users, TrendingUp, Package, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import DashboardLayout from '@/components/DashboardLayout';

const stats = [
  { title: 'Total Revenue', value: 'ksh84,254.00', change: '+12.5%', isPositive: true, icon: DollarSign },
  { title: 'Total Orders', value: '1,432', change: '+8.2%', isPositive: true, icon: ShoppingCart },
  { title: 'Active Customers', value: '3,842', change: '+5.4%', isPositive: true, icon: Users },
  { title: 'Conversion Rate', value: '2.4%', change: '-0.8%', isPositive: false, icon: TrendingUp },
];

const recentOrders = [
  { id: '#ORD-1234', product: 'Wireless Headphones', amount: 'ksh129.99', status: 'Completed' },
  { id: '#ORD-1235', product: 'Smart Watch', amount: 'ksh299.99', status: 'Processing' },
  { id: '#ORD-1236', product: 'Laptop Stand', amount: 'ksh49.99', status: 'Completed' },
  { id: '#ORD-1237', product: 'USB-C Hub', amount: 'ksh79.99', status: 'Pending' },
];

const topProducts = [
  { name: 'Wireless Earbuds Pro', sales: 324, revenue: 'ksh45,360' },
  { name: 'Smart Watch Elite', sales: 256, revenue: 'ksh76,800' },
  { name: 'Ultra HD Monitor', sales: 186, revenue: 'ksh55,800' },
  { name: 'Ergonomic Keyboard', sales: 145, revenue: 'ksh14,500' },
];

function App() {
  return (
    <DashboardLayout>
      <div className="flex flex-col flex-wrap sm:h-[100vh] sm:w-[100vw] bg-gray-50 overflow-auto">

        {/* Main Content */}
        <div className="flex-1 mt-0">
          {/* Header */}
          <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">Last updated: {new Date().toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </header>

          {/* Dashboard Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat) => (
                <div key={stat.title} className="bg-white rounded-lg shadow-sm p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <stat.icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <span className={`flex items-center text-sm ${stat.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                      {stat.change}
                      {stat.isPositive ? (
                        <ArrowUpRight className="w-4 h-4 ml-1" />
                      ) : (
                        <ArrowDownRight className="w-4 h-4 ml-1" />
                      )}
                    </span>
                  </div>
                  <h3 className="text-gray-500 text-sm font-medium">{stat.title}</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chart Section */}
              <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Revenue Overview</h2>
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                </div>
                <div className="h-64 flex items-center justify-center text-gray-400">
                  Chart placeholder - Revenue data visualization would go here
                </div>
              </div>

              {/* Top Products */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Top Products</h2>
                  <Package className="w-5 h-5 text-gray-400" />
                </div>
                <div className="space-y-4">
                  {topProducts.map((product) => (
                    <div key={product.name} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{product.name}</p>
                        <p className="text-sm text-gray-500">{product.sales} sales</p>
                      </div>
                      <p className="text-sm font-semibold text-gray-900">{product.revenue}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent Orders */}
            <div className="mt-6 bg-white rounded-lg shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Recent Orders</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Order ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Product
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recentOrders.map((order) => (
                      <tr key={order.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {order.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {order.product}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {order.amount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                            ${order.status === 'Completed' ? 'bg-green-100 text-green-800' : 
                              order.status === 'Processing' ? 'bg-blue-100 text-blue-800' : 
                              'bg-yellow-100 text-yellow-800'}`}>
                            {order.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </main>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default App;
