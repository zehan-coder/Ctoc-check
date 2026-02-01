import {
  Zap,
  Shield,
  BarChart3,
  Bot,
  Users,
  Globe,
  Clock,
  Settings,
  MessageSquare,
  Target,
  ZapOff,
  CheckCircle
} from "lucide-react";

export default function FeaturesSection() {
  const features = [
    {
      icon: Zap,
      title: "Instant Server Boosts",
      description: "Get instant server boosts with our automated delivery system. No waiting, no hassle.",
      color: "from-primary-500 to-primary-600"
    },
    {
      icon: Shield,
      title: "Advanced Security",
      description: "Enterprise-grade security with 2FA, role-based access, and audit logs.",
      color: "from-green-500 to-green-600"
    },
    {
      icon: BarChart3,
      title: "Real-time Analytics",
      description: "Track your server growth, member engagement, and performance metrics in real-time.",
      color: "from-purple-500 to-purple-600"
    },
    {
      icon: Bot,
      title: "Custom Bots",
      description: "Deploy custom bots tailored to your server's needs with our bot builder.",
      color: "from-blue-500 to-blue-600"
    },
    {
      icon: Users,
      title: "Member Management",
      description: "Powerful tools to manage members, roles, permissions, and moderation.",
      color: "from-orange-500 to-orange-600"
    },
    {
      icon: Globe,
      title: "Multi-Server Support",
      description: "Manage multiple Discord servers from a single dashboard with ease.",
      color: "from-pink-500 to-pink-600"
    },
    {
      icon: Clock,
      title: "Scheduled Tasks",
      description: "Automate repetitive tasks with our powerful scheduling and automation tools.",
      color: "from-teal-500 to-teal-600"
    },
    {
      icon: Settings,
      title: "Customizable Dashboard",
      description: "Personalize your dashboard with widgets, themes, and custom layouts.",
      color: "from-indigo-500 to-indigo-600"
    },
    {
      icon: MessageSquare,
      title: "Live Chat Support",
      description: "Get help when you need it with our 24/7 live chat support team.",
      color: "from-red-500 to-red-600"
    }
  ];

  return (
    <section id="features" className="py-24 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-primary-50 rounded-full px-4 py-2 mb-6">
            <Target className="h-4 w-4 text-primary-600" />
            <span className="text-sm font-semibold text-primary-900">Features</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Everything You Need
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Powerful features to help you manage and grow your Discord community
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-8 rounded-2xl border border-gray-200 hover:border-primary-300 hover:shadow-xl hover:shadow-primary-500/10 transition-all duration-300 bg-white"
            >
              <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-primary-50 to-primary-100 rounded-2xl px-8 py-4">
            <CheckCircle className="h-5 w-5 text-primary-600" />
            <span className="text-gray-700 font-medium">
              99.9% uptime guarantee • 24/7 support • No hidden fees
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
