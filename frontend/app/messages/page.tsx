import React from "react";
import { MessageCircle } from "lucide-react";
import type { Message } from "@/types/message";
import DashboardLayout from "@/components/DashboardLayout";

export default function MessageList() {
  // Example messages data
  const messages: Message[] = [
    {
      id: "1",
      productId: "1",
      content: "Is this product still available?",
      sender: "John Doe",
      timestamp: new Date("2024-03-10T10:00:00"),
    },
    // Add more sample messages as needed
  ];

  const groupedMessages = messages.reduce((acc, message) => {
    if (!acc[message.productId]) {
      acc[message.productId] = [];
    }
    acc[message.productId].push(message);
    return acc;
  }, {} as Record<string, Message[]>);

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center space-x-4 mb-8">
          <MessageCircle className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Product Messages</h2>
        </div>

        <div className="space-y-8">
          {Object.entries(groupedMessages).map(([productId, messages]) => (
            <div key={productId} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Product ID: {productId}
              </h3>
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className="border-l-4 border-purple-500 pl-4 py-3 bg-gray-50 rounded-r-lg"
                  >
                    <div className="flex justify-between items-start">
                      <span className="font-medium text-gray-900">
                        {message.sender}
                      </span>
                      <span className="text-sm text-gray-500">
                        {message.timestamp.toLocaleDateString()}
                      </span>
                    </div>
                    <p className="mt-2 text-gray-700">{message.content}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
