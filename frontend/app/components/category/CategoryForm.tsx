import React from 'react';
import { FolderPlus } from 'lucide-react';

export default function CategoryForm() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-lg shadow-lg max-w-xl mx-auto">
      <div className="flex items-center space-x-4">
        <FolderPlus className="w-6 h-6 text-green-600" />
        <h2 className="text-2xl font-bold text-gray-900">Add New Category</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="categoryName" className="block text-sm font-medium text-gray-700">
            Category Name
          </label>
          <input
            type="text"
            id="categoryName"
            name="categoryName"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
            required
          />
        </div>

        <div>
          <label htmlFor="categoryDescription" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="categoryDescription"
            name="categoryDescription"
            rows={3}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
            required
          />
        </div>
      </div>

      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        Add Category
      </button>
    </form>
  );
}