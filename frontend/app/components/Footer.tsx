import React from "react"
import { Mail, Phone, MapPin, Facebook, Twitter, Instagram } from "lucide-react"

const Footer = () => {
  return (
    <footer className="bg-white dark:bg-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-0 md:pt-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-16 mb-16">
          <div className="space-y-8">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Easymarket</h3>
              <p className="text-gray-600 dark:text-gray-400 text-lg leading-relaxed">
                Your one-stop shop for all academic needs. Quality products at student-friendly prices.
              </p>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-gray-400 hover:text-black dark:hover:text-white transition-colors">
                <Facebook className="h-6 w-6" />
              </a>
              <a href="#" className="text-gray-400 hover:text-black dark:hover:text-white transition-colors">
                <Twitter className="h-6 w-6" />
              </a>
              <a href="#" className="text-gray-400 hover:text-black dark:hover:text-white transition-colors">
                <Instagram className="h-6 w-6" />
              </a>
            </div>
          </div>

          <div className="space-y-8">
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Links</h4>
            <ul className="space-y-4">
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  About Us
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Student Discounts
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Shipping Policy
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  FAQs
                </a>
              </li>
            </ul>
          </div>

          <div className="space-y-8">
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white">Categories</h4>
            <ul className="space-y-4">
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Textbooks
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Stationery
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Electronics
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors text-lg"
                >
                  Study Accessories
                </a>
              </li>
            </ul>
          </div>

          <div className="space-y-8">
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white">Contact Us</h4>
            <ul className="space-y-6">
              <li className="flex items-start space-x-4">
                <MapPin className="h-6 w-6 text-gray-400 flex-shrink-0 mt-1" />
                <span className="text-gray-600 dark:text-gray-400 text-lg">
                  123, nakuru,
                  <br />
                  University District, ST 12345
                </span>
              </li>
              <li className="flex items-center space-x-4">
                <Phone className="h-6 w-6 text-gray-400 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400 text-lg">(555) 123-4567</span>
              </li>
              <li className="flex items-center space-x-4">
                <Mail className="h-6 w-6 text-gray-400 flex-shrink-0" />
                <span className="text-gray-600 dark:text-gray-400 text-lg">support@EasyMarket.com</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 pt-8 ">
          <p className="text-center text-gray-600 dark:text-gray-400 text-lg">
            © {new Date().getFullYear()} EasyMarket. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer

