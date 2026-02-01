import Link from "next/link";
import { ArrowRight, Github, Mail, Check } from "lucide-react";

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2">
            <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2 rounded-lg">
              <ArrowRight className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
              BoostSync
            </span>
          </Link>
        </div>

        {/* Signup Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Create your account
            </h1>
            <p className="text-gray-600">
              Start boosting your Discord server today
            </p>
          </div>

          {/* Social Signup Buttons */}
          <div className="space-y-4 mb-6">
            <button className="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 rounded-xl py-3 px-4 hover:bg-gray-50 transition-colors">
              <Github className="h-5 w-5" />
              <span className="font-medium text-gray-700">Continue with GitHub</span>
            </button>
            <button className="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 rounded-xl py-3 px-4 hover:bg-gray-50 transition-colors">
              <Mail className="h-5 w-5" />
              <span className="font-medium text-gray-700">Continue with Email</span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">or sign up with email</span>
            </div>
          </div>

          {/* Form */}
          <form className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="••••••••"
              />
            </div>

            {/* Password Requirements */}
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Password must contain:</p>
              <ul className="space-y-1">
                <li className="flex items-center text-sm text-gray-600">
                  <Check className="h-4 w-4 mr-2 text-gray-400" />
                  At least 8 characters
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <Check className="h-4 w-4 mr-2 text-gray-400" />
                  At least one uppercase letter
                </li>
                <li className="flex items-center text-sm text-gray-600">
                  <Check className="h-4 w-4 mr-2 text-gray-400" />
                  At least one number
                </li>
              </ul>
            </div>

            <div className="flex items-start">
              <input
                type="checkbox"
                id="terms"
                name="terms"
                required
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 mt-0.5"
              />
              <label htmlFor="terms" className="ml-2 block text-sm text-gray-700">
                I agree to the{" "}
                <Link href="/terms" className="text-primary-600 hover:text-primary-700 font-medium">Terms of Service</Link>
                {" "}and{" "}
                <Link href="/privacy" className="text-primary-600 hover:text-primary-700 font-medium">Privacy Policy</Link>
              </label>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-primary-500/25 transition-all duration-200"
            >
              Create account
            </button>
          </form>

          {/* Sign In Link */}
          <p className="mt-6 text-center text-gray-600">
            Already have an account?{" "}
            <Link href="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
              Sign in
            </Link>
          </p>
        </div>

        {/* Free Trial Info */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center space-x-2 bg-primary-50 rounded-full px-4 py-2">
            <span className="text-sm text-primary-700 font-medium">
              14-day free trial • No credit card required
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
