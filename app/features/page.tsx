import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Back Button */}
        <Link
          href="/"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium mb-8"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to home
        </Link>

        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            All Features
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Explore everything BoostSync has to offer
          </p>
        </div>

        {/* Content Placeholder */}
        <div className="text-center py-20">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-100 rounded-full mb-6">
            <span className="text-4xl">🚧</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Under Construction
          </h2>
          <p className="text-gray-600 mb-6">
            This page is being built. Check back soon for the complete features list.
          </p>
          <Link
            href="/"
            className="inline-flex items-center justify-center space-x-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-200"
          >
            <span>Return Home</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
