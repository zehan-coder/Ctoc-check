import Link from "next/link";
import { ArrowLeft, Mail, MessageCircle, BookOpen } from "lucide-react";

export default function SupportPage() {
  const supportOptions = [
    {
      icon: BookOpen,
      title: "Documentation",
      description: "Browse our comprehensive guides and tutorials",
      href: "/docs",
      color: "from-blue-500 to-blue-600"
    },
    {
      icon: MessageCircle,
      title: "Community Discord",
      description: "Join our Discord community for help and discussions",
      href: "https://discord.gg/boostsync",
      color: "from-indigo-500 to-indigo-600"
    },
    {
      icon: Mail,
      title: "Email Support",
      description: "Get in touch with our support team via email",
      href: "mailto:support@boostsync.com",
      color: "from-green-500 to-green-600"
    }
  ];

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
            Need Help?
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            We&apos;re here to help you succeed with BoostSync
          </p>
        </div>

        {/* Support Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {supportOptions.map((option, index) => (
            <a
              key={index}
              href={option.href}
              className="group p-8 rounded-2xl border border-gray-200 hover:border-primary-300 hover:shadow-xl hover:shadow-primary-500/10 transition-all duration-300"
            >
              <div className={`w-14 h-14 bg-gradient-to-br ${option.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                <option.icon className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {option.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {option.description}
              </p>
            </a>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h2>

          <div className="space-y-4">
            <div className="border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                How do I get started with BoostSync?
              </h3>
              <p className="text-gray-600">
                Simply sign up for a free account, connect your Discord server, and start using our features. No credit card required.
              </p>
            </div>

            <div className="border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Is BoostSync free to use?
              </h3>
              <p className="text-gray-600">
                Yes! We offer a free plan with essential features. Premium plans are available for advanced features and more server boosts.
              </p>
            </div>

            <div className="border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                How does the server boosting work?
              </h3>
              <p className="text-gray-600">
                Our automated system delivers server boosts quickly and securely. You can purchase boost packages and they will be applied to your server.
              </p>
            </div>

            <div className="border border-gray-200 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Can I cancel my subscription anytime?
              </h3>
              <p className="text-gray-600">
                Absolutely! You can cancel your subscription at any time from your dashboard settings. No questions asked.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
